#!/usr/bin/env python3
"""
Processador de Dados - VERSÃO PESADA (Ineficiente)
====================================================

Este script simula um processamento de dados de forma INEFICIENTE:
- Usa loops aninhados desnecessários
- Aloca muita memória de uma vez
- Operações redundantes e duplicadas
- Sem cache ou otimizações
- Alto uso de CPU e memória

Espera-se nota BAIXA (C ou D) no Score SCI do EcoDash.
"""

import time
import random
from datetime import datetime


def generate_data_inefficient(size: int) -> list:
    """Gera dados de forma INEFICIENTE - aloca tudo na memória."""
    print(f"[{datetime.now().strftime('%H:%M:%S')}] Gerando {size} registros (pesada)...")
    
    # ❌ INEFICIENTE: Aloca toda lista de uma vez
    data = []
    for i in range(size):
        # ❌ INEFICIENTE: Cria lista desnecessária para cada item
        record = {
            "id": i,
            "timestamp": datetime.now().isoformat(),
            "value": random.randint(0, 1000000),
            "category": random.choice(["A", "B", "C", "D", "E"] * 1000),  # ❌ Lista gigante repetida
            "metadata": [random.random() for _ in range(100)],  # ❌ 100 floats por registro
            "tags": [f"tag_{j}" for j in range(50)],  # ❌ 50 strings por registro
        }
        data.append(record)
        
        # ❌ INEFICIENTE: Operações desnecessárias no loop principal
        if i % 1000 == 0:
            _ = sum([x ** 2 for x in range(10000)])  # Cálculo inútil
    
    return data


def filter_data_inefficient(data: list) -> list:
    """Filtra dados de forma INEFICIENTE."""
    print(f"[{datetime.now().strftime('%H:%M:%S')}] Filtrando dados (método pesado)...")
    
    filtered = []
    
    # ❌ INEFICIENTE: Múltiplos loops sobre os mesmos dados
    for i in range(len(data)):
        for j in range(len(data)):
            if data[i]["id"] == data[j]["id"] and data[i]["value"] > 500000:
                if data[i] not in filtered:  # ❌ Busca O(n) no final da lista
                    filtered.append(data[i])
                break
    
    # ❌ INEFICIENTE: Segunda passagem desnecessária
    result = []
    for record in filtered:
        # ❌ INEFICIENTE: Recria objetos completamente
        new_record = {
            "id": record["id"],
            "timestamp": record["timestamp"],
            "value": record["value"],
            "category": record["category"],
            "metadata": [x * 2 for x in record["metadata"]],  # Recalcula tudo
            "tags": record["tags"] + ["processed"],
        }
        result.append(new_record)
    
    return result


def aggregate_data_inefficient(data: list) -> dict:
    """Agrega dados de forma INEFICIENTE."""
    print(f"[{datetime.now().strftime('%H:%M:%S')}] Agregando dados (método pesado)...")
    
    # ❌ INEFICIENTE: Cria lista de dicionários intermediários
    stats_by_category = {}
    
    # ❌ INEFICIENTE: Múltiplos loops sobre os mesmos dados
    for record in data:
        category = record["category"]
        
        # ❌ INEFICIENTE: Se categoria não existe, refaz toda computação
        if category not in stats_by_category:
            # Loop completo novamente só para essa categoria
            matching = [r for r in data if r["category"] == category]
            values = [r["value"] for r in matching]
            
            stats_by_category[category] = {
                "count": len(matching),
                "sum": sum(values),
                "avg": sum(values) / len(values) if values else 0,
                "min": min(values) if values else 0,
                "max": max(values) if values else 0,
                "median": sorted(values)[len(values) // 2] if values else 0,
                "variance": sum((x - sum(values) / len(values)) ** 2 for x in values) / len(values) if values else 0,
                "stddev": (sum((x - sum(values) / len(values)) ** 2 for x in values) / len(values)) ** 0.5 if values else 0,
            }
    
    # ❌ INEFICIENTE: Operações redundantes de formatação
    result = {}
    for category, stats in stats_by_category.items():
        # ❌ INEFICIENTE: Recalcula tudo novamente
        result[category] = {
            "count": stats["count"],
            "sum": stats["sum"],
            "average": stats["avg"],
            "minimum": stats["min"],
            "maximum": stats["max"],
            "median_value": stats["median"],
            "variance_value": stats["variance"],
            "stddev_value": stats["stddev"],
            "formatted_avg": f"{stats['avg']:.2f}",
            "formatted_sum": f"{stats['sum']:.0f}",
            "percentile_95": sorted([r["value"] for r in data if r["category"] == category])[
                int(0.95 * len([r for r in data if r["category"] == category]))
            ] if len([r for r in data if r["category"] == category]) > 0 else 0,
        }
    
    return result


def duplicate_processing(data: list) -> list:
    """Processa dados DUPLICADAMENTE - simula processamento redundante."""
    print(f"[{datetime.now().strftime('%H:%M:%S')}] Processamento redundante (pesado)...")
    
    # ❌ INEFICIENTE: Processa os mesmos dados várias vezes desnecessariamente
    processed = []
    
    for _ in range(3):  # ❌ Processa 3 vezes!
        for record in data:
            # ❌ INEFICIENTE: Operações custosas por registro
            heavy_computation = {
                "hash": hash(str(record)),
                "transformed": record["value"] * 3.14159,
                "recursive_calc": fibonacci_slow(15),  # Cálculo exponencial!
                "string_ops": f"{record['id']:010d}_{record['value']:020d}" * 10,
            }
            processed.append(heavy_computation)
    
    return processed


def fibonacci_slow(n: int) -> int:
    """❌ Implementação LENTA de Fibonacci (recursiva sem memoização)."""
    if n <= 1:
        return n
    return fibonacci_slow(n - 1) + fibonacci_slow(n - 2)


def main():
    """Executa o processamento completo (PESADO)."""
    start_time = time.time()
    print("\n" + "=" * 70)
    print("PROCESSADOR DE DADOS - VERSÃO PESADA (INEFICIENTE)")
    print("=" * 70)
    print(f"Início: {datetime.now().strftime('%H:%M:%S')}\n")
    
    # Gerar dados
    data = generate_data_inefficient(size=5000)
    print(f"✓ Dados gerados: {len(data)} registros\n")
    
    # Filtrar
    filtered = filter_data_inefficient(data)
    print(f"✓ Dados filtrados: {len(filtered)} registros\n")
    
    # Agregar
    stats = aggregate_data_inefficient(filtered)
    print(f"✓ Dados agregados: {len(stats)} categorias\n")
    
    # Processamento redundante
    processed = duplicate_processing(filtered)
    print(f"✓ Processamento redundante: {len(processed)} items\n")
    
    # Exibir resultados
    print("\n" + "=" * 70)
    print("RESUMO DOS RESULTADOS")
    print("=" * 70)
    print(f"Total de registros originais: {len(data)}")
    print(f"Total de registros filtrados: {len(filtered)}")
    print(f"Categorias agregadas: {len(stats)}")
    print(f"\nEstatísticas por categoria (3 primeiras):")
    for i, (category, stat) in enumerate(list(stats.items())[:3]):
        print(f"\n  {category}:")
        print(f"    - Count: {stat['count']}")
        print(f"    - Avg: {stat['average']:.2f}")
        print(f"    - Min: {stat['minimum']}")
        print(f"    - Max: {stat['maximum']}")
    
    elapsed = time.time() - start_time
    print("\n" + "=" * 70)
    print(f"Tempo total: {elapsed:.2f} segundos")
    print(f"Fim: {datetime.now().strftime('%H:%M:%S')}")
    print("=" * 70)
    print("\n⚠️  NOTA ESPERADA: C ou D (Ineficiente)")
    print("Problemas: Alto uso de CPU, memória excessiva, processamento redundante\n")


if __name__ == "__main__":
    main()
