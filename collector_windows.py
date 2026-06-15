#!/usr/bin/env python3
"""
ecodash-collector — versão Windows standalone
Gerado como executável via PyInstaller (sem Python necessário para o usuário).

Lê configuração de ecodash.conf no mesmo diretório do executável.

Uso:
    ecodash-collector.exe python meu_app.py
    ecodash-collector.exe node server.js
"""

import sys
import os
import time
import json
import subprocess
import threading
import configparser
from dataclasses import dataclass, asdict
from datetime import datetime
from pathlib import Path
from typing import List, Optional

try:
    import psutil
    import requests as _requests
except ImportError as e:
    print(f"Erro interno: {e}")
    input("Pressione Enter para fechar...")
    sys.exit(1)


def _read_config() -> tuple[str, str]:
    """Lê token e URL do ecodash.conf no mesmo diretório do executável."""
    if getattr(sys, 'frozen', False):
        base = Path(sys.executable).parent
    else:
        base = Path(__file__).parent

    conf_path = base / "ecodash.conf"
    if not conf_path.exists():
        print(f"\n[ERRO] Arquivo de configuração não encontrado: {conf_path}")
        print("Baixe o arquivo ecodash.conf em: EcoDash > Análise > Download Config")
        print("Coloque-o na mesma pasta que o executável.\n")
        input("Pressione Enter para fechar...")
        sys.exit(1)

    cfg = configparser.ConfigParser()
    cfg.read(conf_path, encoding="utf-8")
    try:
        token = cfg["ecodash"]["token"]
        api_url = cfg["ecodash"]["api_url"].rstrip("/")
    except KeyError as e:
        print(f"\n[ERRO] Chave ausente no ecodash.conf: {e}")
        input("Pressione Enter para fechar...")
        sys.exit(1)

    return token, api_url


ECODASH_TOKEN, ECODASH_API_URL = _read_config()

GRID_INTENSITY = {
    "BR": 100.0, "US": 386.0, "EU": 295.0, "DE": 350.0, "FR": 58.0,
    "CN": 557.0, "IN": 632.0, "AU": 480.0, "GB": 233.0, "GLOBAL": 490.0,
}
EMBODIED_CARBON_PER_HOUR = {
    "laptop": 0.16, "desktop": 0.45, "server": 2.00, "cloud_vm": 0.80,
}
SCI_THRESHOLDS = {
    "AAA": (0, 0.1), "AA": (0.1, 0.5), "A": (0.5, 2.0),
    "B": (2.0, 10.0), "C": (10.0, 50.0), "D": (50.0, float("inf")),
}


@dataclass
class HardwareProfile:
    tdp_watts: float
    hardware_type: str
    cpu_count: int
    memory_total_gb: float


@dataclass
class ExecutionMetrics:
    duration_seconds: float
    cpu_percent_avg: float
    cpu_percent_peak: float
    memory_used_mb_avg: float
    memory_used_mb_peak: float
    io_read_mb: float
    io_write_mb: float
    threads_count: int
    process_name: str
    pid: int


@dataclass
class SCIResult:
    energy_kwh: float
    grid_intensity_gco2_kwh: float
    embodied_carbon_gco2: float
    functional_unit: float
    sci_score: float
    grade: str
    label: str
    region: str
    hardware_type: str
    timestamp: str
    software_name: str
    metrics: dict


def detect_hardware() -> HardwareProfile:
    cpu_count = psutil.cpu_count(logical=False) or 1
    memory_gb = psutil.virtual_memory().total / (1024 ** 3)
    tdp = 45.0 if cpu_count <= 4 else 95.0 if cpu_count <= 8 else 150.0
    hw_type = "desktop" if memory_gb > 16 or cpu_count > 8 else "laptop"
    return HardwareProfile(
        tdp_watts=tdp, hardware_type=hw_type,
        cpu_count=cpu_count, memory_total_gb=round(memory_gb, 2),
    )


def collect_metrics(command: List[str], timeout: Optional[float] = None) -> ExecutionMetrics:
    cpu_samples, mem_samples = [], []
    peak_threads = 0

    proc = subprocess.Popen(
        command, stdout=subprocess.PIPE, stderr=subprocess.STDOUT,
        text=True, creationflags=subprocess.CREATE_NO_WINDOW if sys.platform == "win32" else 0,
    )
    ps_proc = psutil.Process(proc.pid)
    start_time = time.perf_counter()
    try:
        start_io = ps_proc.io_counters() if hasattr(ps_proc, "io_counters") else None
    except Exception:
        start_io = None

    def _sample():
        nonlocal peak_threads
        while proc.poll() is None:
            try:
                ps = psutil.Process(proc.pid)
                cpu_samples.append(ps.cpu_percent(interval=None))
                mem_samples.append(ps.memory_info().rss / (1024 ** 2))
                peak_threads = max(peak_threads, ps.num_threads())
            except (psutil.NoSuchProcess, psutil.AccessDenied):
                break
            time.sleep(0.2)

    threading.Thread(target=_sample, daemon=True).start()
    try:
        for _ in proc.stdout:
            pass
    except Exception:
        pass
    try:
        proc.wait(timeout=timeout)
    except subprocess.TimeoutExpired:
        proc.kill()

    duration = time.perf_counter() - start_time
    io_read_mb = io_write_mb = 0.0
    try:
        end_io = ps_proc.io_counters() if hasattr(ps_proc, "io_counters") else None
        if start_io and end_io:
            io_read_mb = (end_io.read_bytes - start_io.read_bytes) / (1024 ** 2)
            io_write_mb = (end_io.write_bytes - start_io.write_bytes) / (1024 ** 2)
    except Exception:
        pass

    return ExecutionMetrics(
        duration_seconds=round(duration, 4),
        cpu_percent_avg=round(sum(cpu_samples) / len(cpu_samples) if cpu_samples else 0.0, 2),
        cpu_percent_peak=round(max(cpu_samples) if cpu_samples else 0.0, 2),
        memory_used_mb_avg=round(sum(mem_samples) / len(mem_samples) if mem_samples else 0.0, 2),
        memory_used_mb_peak=round(max(mem_samples) if mem_samples else 0.0, 2),
        io_read_mb=round(io_read_mb, 3),
        io_write_mb=round(io_write_mb, 3),
        threads_count=peak_threads,
        process_name=command[0],
        pid=proc.pid,
    )


def calculate_sci(
    metrics: ExecutionMetrics,
    hardware: HardwareProfile,
    region: str = "BR",
    functional_unit: float = 1.0,
) -> SCIResult:
    duration_h = metrics.duration_seconds / 3600.0
    cpu_fraction = metrics.cpu_percent_avg / 100.0
    cpu_energy_kwh = hardware.tdp_watts * cpu_fraction * duration_h / 1000.0
    dram_power_w = (hardware.memory_total_gb / 8.0) * 3.0
    mem_fraction = min(metrics.memory_used_mb_avg / (hardware.memory_total_gb * 1024), 1.0)
    mem_energy_kwh = dram_power_w * mem_fraction * duration_h / 1000.0
    energy_kwh = cpu_energy_kwh + mem_energy_kwh
    grid_intensity = GRID_INTENSITY.get(region.upper(), GRID_INTENSITY["GLOBAL"])
    operational_gco2 = energy_kwh * grid_intensity
    embodied_rate = EMBODIED_CARBON_PER_HOUR.get(hardware.hardware_type, 0.16)
    cpu_share = min(cpu_fraction, 1.0 / max(hardware.cpu_count, 1))
    embodied_gco2 = embodied_rate * duration_h * cpu_share
    sci_score = (operational_gco2 + embodied_gco2) / functional_unit
    grade = next((g for g, (lo, hi) in SCI_THRESHOLDS.items() if lo <= sci_score < hi), "D")
    label = f"{grade} - Green Software" if grade in ("AAA", "AA", "A") else f"{grade} - Requer Melhoria"
    return SCIResult(
        energy_kwh=round(energy_kwh, 8),
        grid_intensity_gco2_kwh=grid_intensity,
        embodied_carbon_gco2=round(embodied_gco2, 6),
        functional_unit=functional_unit,
        sci_score=round(sci_score, 6),
        grade=grade, label=label,
        region=region.upper(), hardware_type=hardware.hardware_type,
        timestamp=datetime.now().isoformat(),
        software_name=metrics.process_name, metrics=asdict(metrics),
    )


def submit(result: dict) -> bool:
    try:
        r = _requests.post(
            f"{ECODASH_API_URL}/api/analyses/",
            json=result,
            headers={"X-Collector-Token": ECODASH_TOKEN},
            timeout=10,
        )
        r.raise_for_status()
        data = r.json()
        print(f"OK  Análise #{data['id']} registrada")
        print(f"    Grade: {data['grade']} | SCI: {data['sci_score']:.6f} gCO2eq")
        print(f"    Ver em: {ECODASH_API_URL}/analise/{data['id']}")
        return True
    except Exception as e:
        print(f"ERRO ao enviar para EcoDash: {e}")
        fallback = Path.cwd() / "ecodash-result.json"
        with open(fallback, "w", encoding="utf-8") as f:
            json.dump(result, f, indent=2, ensure_ascii=False)
        print(f"    Resultado salvo em: {fallback}")
        return False


def main():
    print("=" * 55)
    print("  EcoDash Collector — Windows")
    print("=" * 55)

    if len(sys.argv) < 2:
        print("\nUso:  ecodash-collector.exe <comando> [args...]")
        print("Ex:   ecodash-collector.exe python meu_app.py")
        print("      ecodash-collector.exe node server.js")
        print()
        input("Pressione Enter para fechar...")
        sys.exit(1)

    command = sys.argv[1:]
    print(f"Medindo:  {' '.join(command)}")
    print("-" * 55)

    hw = detect_hardware()
    print(f"Hardware: {hw.hardware_type} | {hw.cpu_count} núcleos | {hw.memory_total_gb:.1f} GB RAM")
    print("Executando e coletando métricas...")
    print()

    metrics = collect_metrics(command)
    result = calculate_sci(metrics, hw, region="BR")
    result.software_name = " ".join(command)
    result_dict = asdict(result)

    print()
    print("-" * 55)
    print(f"Duração:      {result_dict['metrics']['duration_seconds']:.2f}s")
    print(f"CPU (média):  {result_dict['metrics']['cpu_percent_avg']:.1f}%")
    print(f"RAM (média):  {result_dict['metrics']['memory_used_mb_avg']:.1f} MB")
    print(f"Energia:      {result_dict['energy_kwh']:.8f} kWh")
    print(f"SCI Score:    {result_dict['sci_score']:.6f} gCO2eq")
    print(f"Grade:        {result_dict['grade']}  ({result_dict['label']})")
    print("-" * 55)
    print("Enviando para EcoDash...")
    print()

    submit(result_dict)

    print()
    input("Pressione Enter para fechar...")


if __name__ == "__main__":
    main()
