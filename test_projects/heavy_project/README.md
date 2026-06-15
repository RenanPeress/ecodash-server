# 🚫 Projeto Pesado - Versão Ineficiente

## Descrição

Este projeto é uma **versão deliberadamente ineficiente** de um processador de dados. Ele foi projetado para demonstrar práticas ruins de programação que resultam em alto consumo de recursos.

## 🔴 Problemas de Performance

- ❌ **Loops aninhados desnecessários**: O(n²) onde poderia ser O(n)
- ❌ **Alocação excessiva de memória**: Aloca tudo de uma vez na RAM
- ❌ **Operações redundantes**: Processa os mesmos dados 3 vezes
- ❌ **Sem caching**: Recalcula os mesmos valores repetidamente
- ❌ **Algoritmos lentos**: Fibonacci recursivo sem memoização (exponencial)
- ❌ **Estruturas ineficientes**: Lista com busca O(n) ao invés de set/dict
- ❌ **Processamento excessivo**: Metadata gigante (100 floats + 50 strings por registro)

## 📊 Métricas Esperadas

- **Tempo de execução**: ~10-20 segundos
- **Uso de CPU**: Alto e sustentado
- **Uso de Memória**: ~500MB+ 
- **Score SCI**: **C ou D** (Ineficiente - Alto impacto ambiental)

## 🚀 Como Executar

```bash
python data_processor_heavy.py
```

## 📋 O que o Script Faz

1. **Gera 5.000 registros** com metadata excessiva
2. **Filtra** usando loops aninhados (O(n²))
3. **Agrega** recalculando tudo para cada categoria
4. **Processa redundantemente** 3 vezes a mesma coisa
5. **Exibe estatísticas** dos resultados

## 💡 Para Comparação

Compare este projeto com `optimized_project/` para ver a mesma funcionalidade implementada de forma eficiente.
