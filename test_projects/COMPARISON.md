# 📊 Análise Comparativa - Projeto Pesado vs Otimizado

## 🔄 Mesma Funcionalidade, Implementações Diferentes

Ambos os projetos realizam a mesma tarefa:
1. Gerar 5.000 registros de dados
2. Filtrar registros com valor > 500.000
3. Agrupar por categoria
4. Calcular estatísticas (count, sum, avg, min, max, variance, stddev)
5. Exibir resultados

**A diferença está em COMO fazem isso.**

---

## ❌ Projeto Pesado (heavy_project)

### 📝 Implementação

| Aspecto | Implementação |
|---------|---|
| Geração de Dados | Aloca lista completa de 5.000 objetos na memória |
| Metadados | Cada registro tem 100 floats + 50 strings (BLOAT) |
| Filtragem | Usa 2 loops aninhados (O(n²)) |
| Busca | Usa `.in` em lista (O(n) por busca) |
| Agregação | Recalcula tudo para cada categoria (O(n) x n_categorias) |
| Processamento Extra | Executa processamento 3 vezes! |
| Fibonacci | Recursão sem cache (exponencial: 2^n) |
| Estruturas | Listas, lists, lists (ineficiente) |

### 📊 Resultados Esperados

```
Tempo de Execução: ████████████ 10-20 segundos
Uso de Memória:   ████████████ ~500MB+
Uso de CPU:       ████████████ Alto e sustentado
SCI Score:        ████████████ C ou D
```

### ⚠️ Problemas

```python
# ❌ Aloca 5.000 dicts gigantes de uma vez
data = []
for i in range(5000):
    record = {
        "id": i,
        "metadata": [random.random() for _ in range(100)],  # 100 floats!
        "tags": [f"tag_{j}" for j in range(50)],            # 50 strings!
    }
    data.append(record)  # Todos na memória

# ❌ Loop aninhado O(n²) para filtrar
for i in range(len(data)):
    for j in range(len(data)):  # De novo?!
        if data[i]["id"] == data[j]["id"]:

# ❌ Recalcula tudo para cada categoria
for category in categories:
    matching = [r for r in data if r["category"] == category]  # Re-itera tudo
    for record in matching:  # De novo

# ❌ Fibonacci exponencial
def fibonacci_slow(n):
    return fibonacci_slow(n-1) + fibonacci_slow(n-2)  # 2^n chamadas!
```

---

## ✅ Projeto Otimizado (optimized_project)

### 📝 Implementação

| Aspecto | Implementação |
|---------|---|
| Geração de Dados | Generator - aloca um registro por vez |
| Metadados | Apenas dados essenciais (sem bloat) |
| Filtragem | Um único loop (O(n)) |
| Busca | Usa dict/defaultdict (O(1)) |
| Agregação | Um loop por categoria (O(n)) |
| Processamento Extra | Executa apenas uma vez |
| Fibonacci | Com cache LRU (O(n)) |
| Estruturas | Dict, defaultdict, generators (eficiente) |

### 📊 Resultados Esperados

```
Tempo de Execução: ██ 0.5-2 segundos (10-20x MAIS RÁPIDO!)
Uso de Memória:   ██ ~10-20MB (25x MENOS!)
Uso de CPU:       ██ Baixo e breve
SCI Score:        ██ A ou AA
```

### ✅ Otimizações

```python
# ✅ Generator - aloca um registro por vez
def generate_data_efficient(size):
    for i in range(size):
        yield {
            "id": i,
            "value": (i * 7919) % 1000000,  # Determinístico, compacto
            "category": ["A", "B", "C", "D", "E"][i % 5],  # Reutiliza lista
        }

# ✅ Um loop O(n) para filtrar e agrupar
grouped = defaultdict(list)
for record in data:
    if record["value"] > 500000:  # Filtra
        grouped[record["category"]].append(record)  # Agrupa

# ✅ Um loop por categoria
for category, records in grouped.items():
    values = [r["value"] for r in records]
    stats[category] = {
        "sum": sum(values),
        "avg": sum(values) / len(values),
    }

# ✅ Fibonacci com cache (memoização)
@lru_cache(maxsize=128)
def fibonacci_fast(n):
    return fibonacci_fast(n-1) + fibonacci_fast(n-2)  # O(n) com cache
```

---

## 🔍 Comparação Linha por Linha

### Geração de Dados

#### ❌ Pesado
```python
# Aloca lista gigante de uma vez
data = []
for i in range(5000):
    record = {
        "id": i,
        "value": random.randint(0, 1000000),
        "category": random.choice(["A", "B", "C", "D", "E"] * 1000),  # Lista de 5000 strings!
        "metadata": [random.random() for _ in range(100)],  # 100 floats
        "tags": [f"tag_{j}" for j in range(50)],  # 50 strings
    }
    data.append(record)
```
**Custo:** ~500MB na memória para 5.000 registros

#### ✅ Otimizado
```python
# Generator - um por vez
def generate_data_efficient(size):
    for i in range(size):
        yield {
            "id": i,
            "value": (i * 7919) % 1000000,
            "category": ["A", "B", "C", "D", "E"][i % 5],  # Reutiliza
        }
```
**Custo:** ~50 bytes por registro (gerado sob demanda)

---

### Filtragem e Agrupamento

#### ❌ Pesado
```python
# 2 loops aninhados: O(n²) = 25 milhões de operações!
filtered = []
for i in range(len(data)):  # 5.000
    for j in range(len(data)):  # 5.000 de novo!
        if data[i]["id"] == data[j]["id"]:
            if data[i] not in filtered:  # Busca O(n) em lista
                filtered.append(data[i])
```
**Complexidade:** O(n²) + O(n) = ~25 milhões de comparações

#### ✅ Otimizado
```python
# Um loop: O(n)
grouped = defaultdict(list)
for record in data:  # 5.000
    if record["value"] > 500000:
        grouped[record["category"]].append(record)  # O(1) com dict
```
**Complexidade:** O(n) = ~5.000 operações

---

### Agregação Estatística

#### ❌ Pesado
```python
# Para cada categoria, re-itera TODA a lista
stats = {}
for category in categories:  # 5 categorias
    matching = [r for r in data if r["category"] == category]  # O(n)
    values = [r["value"] for r in matching]  # O(n)
    
    # Calcula tudo de novo
    sum_val = sum(values)
    avg = sum_val / len(values)
    variance = sum((x - avg) ** 2 for x in values) / len(values)
    # ... e mais 6 estatísticas
```
**Complexidade:** O(n) × n_categorias × n_stats = ~80.000 operações

#### ✅ Otimizado
```python
# Já está agrupado, apenas itera grupos
stats = {}
for category, records in grouped.items():  # 5 categorias
    values = [r["value"] for r in records]  # Já filtrado!
    avg = sum(values) / len(values)  # Uma passa
    variance = sum((x - avg) ** 2 for x in values) / len(values)  # Uma passa
```
**Complexidade:** O(n) = ~5.000 operações

---

## 📈 Resumo de Impacto

### Consumo de Memória
```
Pesado:      [████████████████████████] ~500MB
Otimizado:   [██] ~10-20MB
Diferença:   25x MENOS MEMÓRIA
```

### Tempo de Execução
```
Pesado:      [████████████████████████] 10-20s
Otimizado:   [██] 0.5-2s
Diferença:   10-20x MAIS RÁPIDO
```

### Número de Operações
```
Pesado:      ~26 milhões
Otimizado:   ~10.000
Diferença:   2.600x MENOS OPERAÇÕES
```

### Score SCI (Green Software)
```
Pesado:      [D] 50-100 gCO2/GB  ❌
Otimizado:   [A] 0.5-2 gCO2/GB   ✅
Diferença:   50-100x MENOS IMPACTO AMBIENTAL
```

---

## 💡 Lições Aprendidas

### ❌ Erros Comuns no Código Pesado

1. **Alocação Desnecessária**: Criar lista de 5.000 objetos quando generator seria suficiente
2. **Loops Aninhados**: O(n²) quando deveria ser O(n)
3. **Redundância**: Processar mesmos dados 3 vezes
4. **Metadados Excessivos**: 100 floats + 50 strings por registro (bloat)
5. **Sem Cache**: Recalcular valores já conhecidos (Fibonacci exponencial)
6. **Estruturas Ineficientes**: Lista com busca O(n) ao invés de dict O(1)

### ✅ Melhores Práticas no Código Otimizado

1. **Generators**: `yield` para processar sob demanda
2. **Processamento em Lote**: Filtrar, agrupar e agregar no mesmo loop
3. **Sem Redundância**: Cada dado processado apenas uma vez
4. **Minimalismo**: Manter apenas o necessário
5. **Memoização**: Cache para cálculos repetidos
6. **Estruturas Apropriadas**: Dict para lookup O(1)

---

## 🎯 Como Usar Isso

1. **Execute ambos** os scripts e veja as métricas
2. **Compare** o tempo, memória e CPU
3. **Baixe a análise** no EcoDash Dashboard
4. **Identifique** qual versão é mais sustentável
5. **Entenda** POR QUÊ uma é melhor que a outra
6. **Aplique** essas lições no seu código

---

## 📚 Recursos

- [Green Software Foundation](https://greensoftware.foundation)
- [Software Carbon Intensity (SCI) Spec](https://github.com/Green-Software-Foundation/sci)
- [Principles of Green Software Engineering](https://learn.greensoftware.foundation/)

