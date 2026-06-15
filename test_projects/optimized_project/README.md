# ✅ Projeto Otimizado - Versão Eficiente e Sustentável

## Descrição

Este projeto é uma **versão otimizada e eficiente** de um processador de dados. Implementa a mesma funcionalidade que `heavy_project/`, mas com práticas recomendadas de programação sustentável.

## 🟢 Otimizações Implementadas

- ✅ **Generators**: Usa `yield` ao invés de alocar listas inteiras na memória
- ✅ **Processamento em um único passo**: Filtra e agrupa no mesmo loop
- ✅ **Caching (Memoização)**: Função Fibonacci com `@lru_cache`
- ✅ **Algoritmos O(n)**: Evita loops aninhados desnecessários
- ✅ **Estruturas apropriadas**: `defaultdict` ao invés de listas com busca
- ✅ **Sem redundância**: Processa dados apenas UMA vez
- ✅ **Memória mínima**: Apenas dados essenciais, sem metadata desnecessária

## 📊 Métricas Esperadas

- **Tempo de execução**: ~0.5-2 segundos (10x+ mais rápido!)
- **Uso de CPU**: Baixo e breve
- **Uso de Memória**: ~10-20MB (25x+ menos!)
- **Score SCI**: **A ou AA** (Excelente - Baixo impacto ambiental)

## 🚀 Como Executar

```bash
python data_processor_optimized.py
```

## 📋 O que o Script Faz

1. **Gera 5.000 registros** usando generator (sem alocar tudo)
2. **Filtra e agrupa** em um único passo (O(n))
3. **Agrega** com cálculos otimizados
4. **Processa uma única vez** (não redundante)
5. **Exibe estatísticas** dos resultados

## 🔄 Comparação com `heavy_project/`

| Aspecto | Pesado | Otimizado |
|---------|--------|-----------|
| Tempo | 10-20s | 0.5-2s |
| Memória | ~500MB+ | ~10-20MB |
| Loops Aninhados | Sim (O(n²)) | Não (O(n)) |
| Processamento | 3x redundante | 1x apenas |
| Fibonacci | Recursivo lento | Com cache rápido |
| Generators | Não | Sim |
| SCI Score | C ou D | A ou AA |

## 📚 Conceitos de Green Software

Este projeto demonstra:
1. **Eficiência de Algoritmos**: O(n) ao invés de O(n²)
2. **Gestão de Memória**: Generators e estruturas apropriadas
3. **Evitar Redundância**: Processar dados apenas uma vez
4. **Caching**: Reutilizar cálculos já feitos
5. **Minimismo**: Manter apenas dados necessários

