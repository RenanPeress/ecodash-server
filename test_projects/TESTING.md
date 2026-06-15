# 🧪 Scripts de Teste

Scripts para testar automaticamente ambos os projetos com o EcoDash Collector.

## 📋 Arquivos

- `test_both_projects.bat` - Para **Windows** (com ecodash-collector.exe)
- `test_both_projects.sh` - Para **Linux/macOS** (com ecodash-collector.py)

## 🚀 Uso

### Windows
```batch
test_both_projects.bat
```

Ou execute manualmente:
```batch
ecodash-collector.exe heavy_project/data_processor_heavy.py
ecodash-collector.exe optimized_project/data_processor_optimized.py
```

### Linux/macOS
```bash
chmod +x test_both_projects.sh
./test_both_projects.sh
```

Ou execute manualmente:
```bash
python3 ecodash-collector.py heavy_project/data_processor_heavy.py
python3 ecodash-collector.py optimized_project/data_processor_optimized.py
```

## ⚠️ Pré-requisitos

1. Baixe o script coletor do EcoDash Server:
   - Windows: `ecodash-collector.exe`
   - Linux/macOS: `ecodash-collector.py`

2. Coloque o script no **mesmo diretório** que este arquivo

3. Configure seu **token de usuário** (normalmente no arquivo de config)

## 📊 O que Esperar

### Teste 1 - Versão Pesada
- ⏱️  Demora **10-20 segundos**
- Usa muita **CPU e memória**
- Resultado: Score **C ou D**

### Teste 2 - Versão Otimizada
- ⏱️  Demora **0.5-2 segundos** (10x+ rápido!)
- Usa pouca **CPU e memória**
- Resultado: Score **A ou AA**

## 🎯 Próximos Passos

1. Execute os testes
2. Verifique o **dashboard EcoDash**
3. Compare as **métricas e scores**
4. Exporte os **relatórios em PDF**
5. Analise as **recomendações de IA**

