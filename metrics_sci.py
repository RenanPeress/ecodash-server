# backend_sci_collector.py

import time
from dataclasses import dataclass, asdict
from datetime import datetime
from typing import List, Optional
import psutil
import subprocess

# =================== CONFIGURAÇÕES SCI =====================

GRID_INTENSITY = {
    "BR": 100.0, "US": 386.0, "EU": 295.0, "DE": 350.0, "FR": 58.0,
    "CN": 557.0, "IN": 632.0, "AU": 480.0, "GB": 233.0, "GLOBAL": 490.0
}

EMBODIED_CARBON_PER_HOUR = {
    "laptop": 0.16, "desktop": 0.45, "server": 2.00, "cloud_vm": 0.80
}

SCI_THRESHOLDS = {
    "AAA": (0, 0.1),
    "AA": (0.1, 0.5),
    "A": (0.5, 2.0),
    "B": (2.0, 10.0),
    "C": (10.0, 50.0),
    "D": (50.0, float("inf"))
}

# =================== DATA CLASSES ==========================

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

# =================== HARDWARE DETECTION ====================

def detect_hardware() -> HardwareProfile:
    cpu_count = psutil.cpu_count(logical=False) or 1
    memory_gb = psutil.virtual_memory().total / (1024 ** 3)
    tdp = 45.0 if cpu_count <= 4 else 95.0 if cpu_count <= 8 else 150.0
    hw_type = "desktop" if memory_gb > 16 or cpu_count > 8 else "laptop"
    return HardwareProfile(tdp_watts=tdp, hardware_type=hw_type,
                           cpu_count=cpu_count, memory_total_gb=round(memory_gb, 2))

# =================== MÉTRICAS DE EXECUÇÃO ==================

def collect_metrics(command: List[str], timeout: Optional[float] = None) -> ExecutionMetrics:
    cpu_samples, mem_samples = [], []
    peak_threads = 0

    proc = subprocess.Popen(command, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True)
    ps_proc = psutil.Process(proc.pid)
    start_time = time.perf_counter()
    start_io = ps_proc.io_counters() if hasattr(ps_proc, "io_counters") else None

    # coleta em loop
    import threading
    def _sample_loop():
        nonlocal peak_threads
        while proc.poll() is None:
            try:
                ps = psutil.Process(proc.pid)
                cpu_samples.append(ps.cpu_percent(interval=None))
                mem_samples.append(ps.memory_info().rss / (1024**2))
                peak_threads = max(peak_threads, ps.num_threads())
            except (psutil.NoSuchProcess, psutil.AccessDenied):
                break
            time.sleep(0.2)

    sampler = threading.Thread(target=_sample_loop, daemon=True)
    sampler.start()

    # consome output para não travar
    for _ in proc.stdout: pass

    try:
        exit_code = proc.wait(timeout=timeout)
    except subprocess.TimeoutExpired:
        proc.kill()
        exit_code = -1

    sampler.join(timeout=1.0)
    duration = time.perf_counter() - start_time

    io_read_mb = io_write_mb = 0.0
    try:
        end_io = ps_proc.io_counters() if hasattr(ps_proc, "io_counters") else None
        if start_io and end_io:
            io_read_mb = (end_io.read_bytes - start_io.read_bytes) / (1024**2)
            io_write_mb = (end_io.write_bytes - start_io.write_bytes) / (1024**2)
    except Exception: pass

    cpu_avg = sum(cpu_samples)/len(cpu_samples) if cpu_samples else 0.0
    cpu_peak = max(cpu_samples) if cpu_samples else 0.0
    mem_avg = sum(mem_samples)/len(mem_samples) if mem_samples else 0.0
    mem_peak = max(mem_samples) if mem_samples else 0.0

    return ExecutionMetrics(
        duration_seconds=round(duration, 4),
        cpu_percent_avg=round(cpu_avg, 2),
        cpu_percent_peak=round(cpu_peak, 2),
        memory_used_mb_avg=round(mem_avg, 2),
        memory_used_mb_peak=round(mem_peak, 2),
        io_read_mb=round(io_read_mb, 3),
        io_write_mb=round(io_write_mb, 3),
        threads_count=peak_threads,
        process_name=command[0],
        pid=proc.pid
    )

# =================== CÁLCULO SCI ==========================

def calculate_sci(metrics: ExecutionMetrics, hardware: HardwareProfile,
                  region: str = "BR", functional_unit: float = 1.0) -> SCIResult:

    duration_h = metrics.duration_seconds / 3600.0
    cpu_fraction = metrics.cpu_percent_avg / 100.0
    cpu_energy_kwh = hardware.tdp_watts * cpu_fraction * duration_h / 1000.0
    dram_power_w = (hardware.memory_total_gb / 8.0) * 3.0
    mem_fraction = min(metrics.memory_used_mb_avg / (hardware.memory_total_gb*1024), 1.0)
    mem_energy_kwh = dram_power_w * mem_fraction * duration_h / 1000.0
    energy_kwh = cpu_energy_kwh + mem_energy_kwh

    grid_intensity = GRID_INTENSITY.get(region.upper(), GRID_INTENSITY["GLOBAL"])
    operational_gco2 = energy_kwh * grid_intensity

    embodied_rate = EMBODIED_CARBON_PER_HOUR.get(hardware.hardware_type, 0.16)
    cpu_share = min(cpu_fraction, 1.0 / max(hardware.cpu_count, 1))
    embodied_gco2 = embodied_rate * duration_h * cpu_share

    sci_score = (operational_gco2 + embodied_gco2) / functional_unit
    grade = next((g for g,(low,high) in SCI_THRESHOLDS.items() if low <= sci_score < high), "D")
    label = f"{grade} - Green Software" if grade in ["AAA","AA","A"] else f"{grade} - Needs Improvement"

    return SCIResult(
        energy_kwh=round(energy_kwh, 8),
        grid_intensity_gco2_kwh=grid_intensity,
        embodied_carbon_gco2=round(embodied_gco2, 6),
        functional_unit=functional_unit,
        sci_score=round(sci_score, 6),
        grade=grade,
        label=label,
        region=region.upper(),
        hardware_type=hardware.hardware_type,
        timestamp=datetime.now().isoformat(),
        software_name=metrics.process_name,
        metrics=asdict(metrics)
    )

# =================== FUNÇÃO PRINCIPAL PARA BACKEND ========

def measure_sci(command: List[str], region: str = "BR",
                functional_unit: float = 1.0,
                tdp: Optional[float] = None,
                hardware_type: Optional[str] = None,
                timeout: Optional[float] = None) -> dict:

    hardware = detect_hardware()
    if tdp: hardware.tdp_watts = tdp
    if hardware_type: hardware.hardware_type = hardware_type

    metrics = collect_metrics(command, timeout=timeout)
    result = calculate_sci(metrics, hardware, region, functional_unit)
    return asdict(result)

# =================== EXEMPLO DE USO ========================

if __name__ == "__main__":
    # Teste local: medir um script de 2s
    result = measure_sci(["python", "-c", "import time; time.sleep(2)"])
    print(result)