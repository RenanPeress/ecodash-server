#!/usr/bin/env python3
"""
Processador de Dados - VERSÃO OTIMIZADA (Eficiente)
====================================================

Este script implementa a MESMA funcionalidade da versão pesada,
mas de forma OTIMIZADA:
- Generators ao invés de listas inteiras
- Cache e memoização
- Algoritmos eficientes (O(n) ao invés de O(n²))
- Estruturas de dados apropriadas (dict, set)
- Minimiza alocações de memória
- Processamento uma única vez

Espera-se nota ALTA (A ou AA) no Score SCI do EcoDash.
"""

import time
from datetime import datetime
from functools import lru_cache
from collections import defaultdict
from typing import Iterator, Dict, List


def generate_data_efficient(size: int) -> Iterator[dict]:
    """Gera dados de forma EFICIENTE - usa generator."""
    print(f"[{datetime.now().strftime('%H:%M:%S')}] Gerando {size} registros (otimizado)...")
    
    # ✅ EFICIENTE: Usa generator ao invés de alocar tudo na memória
    for i in range(size):
        # ✅ EFICIENTE: Apenas dados essenciais, sem bloat
        yield {
            "id": i,
            "value": (i * 7919) % 1000000,  # Determinístico, não aloca lista
            "category": ["A", "B", "C", "D", "E"][i % 5],  # Reutiliza lista pequena
        }


def filter_data_efficient(data: Iterator[dict]) -> Dict[str, list]:
    """Filtra e agrupa dados em UM ÚNICO PASSO."""
    print(f"[{datetime.now().strftime('%H:%M:%S')}] Filtrando e agrupando (otimizado)...")
    
    # ✅ EFICIENTE: Processa em um único loop
    grouped_by_category = defaultdict(list)
    
    for record in data:
        if record["value"] > 500000:  # Filtra
            grouped_by_category[record["category"]].append(record)
    
    return dict(grouped_by_category)


@lru_cache(maxsize=128)
def fibonacci_fast(n: int) -> int:
    """✅ Implementação RÁPIDA de Fibonacci (com memoização)."""
    if n <= 1:
        return n
    return fibonacci_fast(n - 1) + fibonacci_fast(n - 2)


def aggregate_data_efficient(grouped_data: Dict[str, list]) -> dict:
    """Agrega dados de forma EFICIENTE - O(n) ao invés de O(n²)."""
    print(f"[{datetime.now().strftime('%H:%M:%S')}] Agregando dados (otimizado)...")
    
    stats = {}
    
    # ✅ EFICIENTE: Um loop por categoria, calcula tudo de uma vez
    for category, records in grouped_data.items():
        if not records:
            continue
        
        values = [r["value"] for r in records]
        value_count = len(values)
        value_sum = sum(values)
        value_avg = value_sum / value_count
        
        # ✅ EFICIENTE: Calcula variância em um único loop
        variance = sum((x - value_avg) ** 2 for x in values) / value_count if value_count > 0 else 0
        
        stats[category] = {
            "count": value_count,
            "sum": value_sum,
            "average": value_avg,
            "minimum": min(values),
            "maximum": max(values),
        }
    
    return stats


def main():
    """Executa o processamento completo (OTIMIZADO)."""
    start_time = time.time()
    print("\n" + "=" * 70)
    print("PROCESSADOR DE DADOS - VERSÃO OTIMIZADA (EFICIENTE)")
    print("=" * 70)
    print(f"Início: {datetime.now().strftime('%H:%M:%S')}\n")
    
    # ✅ EFICIENTE: Gera dados sob demanda (generator)
    data_generator = generate_data_efficient(size=5000)
    
    # ✅ EFICIENTE: Filtra e agrupa em um único passo
    grouped = filter_data_efficient(data_generator)
    total_filtered = sum(len(v) for v in grouped.values())
    print(f"✓ Dados filtrados e agrupados: {total_filtered} registros\n")
    
    # ✅ EFICIENTE: Agrega com cálculos otimizados
    stats = aggregate_data_efficient(grouped)
    print(f"✓ Dados agregados: {len(stats)} categorias\n")
    
    # ✅ EFICIENTE: Processa apenas UMA VEZ (não 3 vezes como na versão pesada)
    print(f"[{datetime.now().strftime('%H:%M:%S')}] Processamento único (otimizado)...")
    
    # ✅ EFICIENTE: Fibonacci com cache
    fib_result = fibonacci_fast(15)
    
    processed_count = total_filtered
    print(f"✓ Processamento concluído: {processed_count} registros\n")
    
    # Exibir resultados
    print("\n" + "=" * 70)
    print("RESUMO DOS RESULTADOS")
    print("=" * 70)
    print(f"Total de registros filtrados: {total_filtered}")
    print(f"Categorias agregadas: {len(stats)}")
    print(f"\nEstatísticas por categoria:")
    for category, stat in sorted(stats.items()):
        print(f"\n  {category}:")
        print(f"    - Count: {stat['count']}")
        print(f"    - Average: {stat['average']:.2f}")
        print(f"    - Min: {stat['minimum']}")
        print(f"    - Max: {stat['maximum']}")
        print(f"    - Sum: {stat['sum']}")
    
    elapsed = time.time() - start_time
    print("\n" + "=" * 70)
    print(f"Tempo total: {elapsed:.2f} segundos")
    print(f"Fim: {datetime.now().strftime('%H:%M:%S')}")
    print("=" * 70)
    print("\n✅ NOTA ESPERADA: A ou AA (Eficiente e Sustentável)")
    print("Otimizações: Generators, caching, O(n), sem redundância\n")


if __name__ == "__main__":
    main()
