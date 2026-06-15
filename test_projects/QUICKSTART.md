# ⚡ Quick Start Guide

## 🚀 30 Segundos para Começar

### Testar Localmente (Sem EcoDash)
```bash
# Versão Otimizada (muito rápida)
python optimized_project/data_processor_optimized.py

# Versão Pesada (lenta)
python heavy_project/data_processor_heavy.py
```

### Testar com EcoDash (Com Collector)
```bash
# Windows
test_both_projects.bat

# Linux/macOS
chmod +x test_both_projects.sh && ./test_both_projects.sh
```

---

## 📊 O Que Esperar

```
Versão Pesada:    ⏱️ 8-20 segundos | 💾 300MB+ | 📈 Score C/D
Versão Otimizada: ⏱️ <1 segundo   | 💾 10MB   | 📈 Score A/AA
```

---

## 📖 Documentação

| Documento | Conteúdo |
|-----------|----------|
| **SUMMARY.md** | Visão geral (COMECE AQUI) |
| **README.md** | Instruções e contexto |
| **COMPARISON.md** | Análise técnica detalhada |
| **TESTING.md** | Como testar com EcoDash |

---

## 🎯 3 Formas de Usar

### Opção 1: Educacional
Aprenda sobre Green Software comparando as duas versões.

### Opção 2: Demonstração
Use para demonstrar o valor do EcoDash para clientes/colegas.

### Opção 3: Desenvolvimento
Use como referência ao otimizar seu próprio código.

---

## ✅ Checklist

- [ ] Li SUMMARY.md (2 min)
- [ ] Executei ambos os scripts localmente (5 min)
- [ ] Comparei o tempo de execução (1 min)
- [ ] Li COMPARISON.md para entender as diferenças (15 min)
- [ ] Baixei o collector do EcoDash (2 min)
- [ ] Executei ambos com o collector (30 seg)
- [ ] Vi os scores no dashboard (5 min)
- [ ] Li as recomendações de IA (5 min)

**Total: ~30 minutos para entender completamente**

---

## 🔍 Key Insights

```
❌ PESADO                    ✅ OTIMIZADO
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Loops O(n²)                 Loops O(n)
Lista inteira na RAM        Generator sob demanda
Metadata excessiva          Apenas o necessário
3x processamento            1x processamento
Sem cache                   Com @lru_cache
Fibonacci recursivo         Fibonacci memoizado
↓                           ↓
8.19s | 300MB | Score D     0.01s | 10MB | Score AA
```

---

## 🎓 Conceitos-Chave

### Generators
```python
❌ data = [processo() for i in range(10000)]  # Aloca tudo
✅ (processo() for i in range(10000))         # Um por vez
```

### Loops Eficientes
```python
❌ for i in range(n):        # O(n)
     for j in range(n):      # × O(n) = O(n²) ❌❌❌

✅ for item in data:         # O(n) apenas
     grouped[item].append()
```

### Caching
```python
❌ def fib(n): return fib(n-1) + fib(n-2)  # 2^n

✅ @lru_cache
   def fib(n): return fib(n-1) + fib(n-2)  # O(n)
```

---

## 📊 Arquivo de Estrutura

```
test_projects/
├── SUMMARY.md                    ← VOCÊ ESTÁ AQUI
├── README.md                     ← Guia principal
├── COMPARISON.md                 ← Análise técnica
├── TESTING.md                    ← Como testar
│
├── heavy_project/
│   ├── data_processor_heavy.py   ← ❌ Versão Pesada
│   └── README.md
│
├── optimized_project/
│   ├── data_processor_optimized.py ← ✅ Versão Otimizada
│   └── README.md
│
├── test_both_projects.bat        ← Script Windows
└── test_both_projects.sh         ← Script Linux/macOS
```

---

## 🆘 Troubleshooting

### "Python não encontrado"
```bash
# Use python3 em vez de python
python3 optimized_project/data_processor_optimized.py
```

### "ecodash-collector.exe não encontrado"
- Baixe do EcoDash Server (`/api/collector/download/windows/exe/`)
- Coloque no mesmo diretório que `test_both_projects.bat`

### "Permission denied" (Linux/macOS)
```bash
chmod +x test_both_projects.sh
./test_both_projects.sh
```

---

## 📞 Recursos

- [EcoDash Server](../)
- [Green Software Foundation](https://greensoftware.foundation)
- [Software Carbon Intensity Spec](https://github.com/Green-Software-Foundation/sci)

---

**Pronto? Comece executando:**
```bash
python optimized_project/data_processor_optimized.py
python heavy_project/data_processor_heavy.py
```
