#!/bin/bash
# Script para testar ambos os projetos com o EcoDash Collector (Linux/macOS)
# Uso: ./test_both_projects.sh

set -e  # Parar no primeiro erro

echo ""
echo "============================================================================"
echo "  TESTE DE AMBOS OS PROJETOS - ECODASH GREEN SOFTWARE"
echo "============================================================================"
echo ""

# Verificar se o coletor Python existe
if [ ! -f "ecodash-collector.py" ]; then
    echo "Erro: ecodash-collector.py não encontrado!"
    echo "Baixe o arquivo do EcoDash Server."
    exit 1
fi

# Verificar se Python está disponível
if ! command -v python3 &> /dev/null; then
    echo "Erro: Python3 não encontrado!"
    echo "Instale Python 3.8 ou superior."
    exit 1
fi

# Teste 1: Versão Pesada
echo "[1/2] Testando VERSÃO PESADA (ineficiente)..."
echo ""
python3 ecodash-collector.py heavy_project/data_processor_heavy.py
echo ""
echo "✓ Teste da versão pesada concluído!"
echo ""
echo "============================================================================"
echo ""

# Pausa entre testes
echo "Aguardando 2 segundos antes do próximo teste..."
sleep 2

echo ""
# Teste 2: Versão Otimizada
echo "[2/2] Testando VERSÃO OTIMIZADA (eficiente)..."
echo ""
python3 ecodash-collector.py optimized_project/data_processor_optimized.py
echo ""
echo "✓ Teste da versão otimizada concluído!"
echo ""
echo "============================================================================"
echo ""
echo "Testes concluídos! Verifique os resultados no dashboard EcoDash."
echo ""
