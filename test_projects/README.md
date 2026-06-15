# 🌿 EcoDash Test Projects

Dois mini projetos para testar o script coletável baixado do EcoDash.

## 📁 Estrutura

```
test_projects/
├── heavy_project/
│   ├── data_processor_heavy.py      # ❌ Versão INEFICIENTE
│   └── README.md
├── optimized_project/
│   ├── data_processor_optimized.py  # ✅ Versão OTIMIZADA
│   └── README.md
└── README.md (este arquivo)
```

## 🎯 Objetivo

Demonstrar como o **Score SCI** do EcoDash varia significativamente entre:
- Uma implementação **ruim** (alto consumo de recursos)
- Uma implementação **boa** (baixo consumo de recursos)

Ambas realizam a mesma tarefa: processar 5.000 registros de dados, filtrar, agregar e gerar estatísticas.

## 📊 Comparação Esperada

### Heavy Project (Ineficiente)
```
⏱️  Tempo: 10-20 segundos
💾 Memória: ~500MB+
⚡ CPU: Alto uso sustentado
📈 SCI Score: C ou D (Ineficiente)
```

### Optimized Project (Eficiente)
```
⏱️  Tempo: 0.5-2 segundos
💾 Memória: ~10-20MB
⚡ CPU: Baixo e breve
📈 SCI Score: A ou AA (Sustentável)
```

## 🚀 Como Testar

### Opção 1: Testar Diretamente

```bash
# Versão pesada
cd heavy_project
python data_processor_heavy.py

# Versão otimizada
cd ../optimized_project
python data_processor_optimized.py
```

### Opção 2: Testar com EcoDash Collector (Recomendado)

1. **Baixe o script coletor** do EcoDash (do servidor)
2. **Configure o token** do usuário no arquivo de configuração
3. **Execute o script coletor** sobre cada versão:

#### Para a versão pesada:
```bash
# Windows (com .exe)
ecodash-collector.exe heavy_project/data_processor_heavy.py

# Linux/macOS (com Python)
python ecodash-collector.py heavy_project/data_processor_heavy.py
```

#### Para a versão otimizada:
```bash
# Windows (com .exe)
ecodash-collector.exe optimized_project/data_processor_optimized.py

# Linux/macOS (com Python)
python ecodash-collector.py optimized_project/data_processor_optimized.py
```

## 📈 O que Você Verá no Dashboard EcoDash

1. **Duas análises** serão registradas (uma para cada versão)
2. **Scores SCI muito diferentes**:
   - Pesada: ~40-100 gCO2/GB (Nota D ou C)
   - Otimizada: ~0.5-2 gCO2/GB (Nota A ou AA)
3. **Métricas detalhadas**:
   - Tempo de execução
   - Consumo de CPU
   - Consumo de memória
   - Energia estimada
   - Intensidade de carbono

## 💡 Aprendizados

### Problemas Encontrados no Projeto Pesado ❌

1. **Loops aninhados** - O(n²) quando poderia ser O(n)
2. **Alocação excessiva** - Aloca 500MB quando 20MB seria suficiente
3. **Operações redundantes** - Processa os mesmos dados 3 vezes
4. **Sem cache** - Recalcula Fibonacci exponencialmente
5. **Estruturas ineficientes** - Lista com busca O(n) ao invés de dict/set
6. **Metadata gigante** - 100 floats + 50 strings por registro

### Otimizações no Projeto Otimizado ✅

1. **Generators** - `yield` ao invés de alocar listas
2. **Processamento único** - Um loop para filtrar E agregar
3. **Memoização** - `@lru_cache` para cálculos repetidos
4. **Estruturas apropriadas** - `defaultdict` para agrupamento
5. **Algoritmos O(n)** - Sem aninhamento desnecessário
6. **Minimalismo** - Apenas dados necessários

## 🔄 Fluxo de Teste Recomendado

1. Teste a **versão pesada** e observe as métricas ruins
2. Teste a **versão otimizada** e compare os resultados
3. Abra o **dashboard EcoDash** para visualizar ambas as análises
4. Exporte **PDFs comparativos**
5. Use as **recomendações de IA** para entender as diferenças

## 📚 Referências

- [Software Carbon Intensity Spec](https://github.com/Green-Software-Foundation/sci)
- [Green Software Foundation](https://greensoftware.foundation)
- [EcoDash Servidor](../)

## 📝 Notas

- Os scripts são **determinísticos** - rodando novamente dará resultados similares
- O tempo pode variar dependendo da **máquina e carga do sistema**
- O Score SCI também varia por **região** (intensidade de carbono da grid)

---

**Última atualização**: 2026-06-15
