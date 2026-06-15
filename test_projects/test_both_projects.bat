@echo off
REM Script para testar ambos os projetos com o EcoDash Collector (Windows)
REM Certifique-se de que o ecodash-collector.exe está no PATH ou no mesmo diretório

setlocal enabledelayedexpansion

echo.
echo ============================================================================
echo  TESTE DE AMBOS OS PROJETOS - ECODASH GREEN SOFTWARE
echo ============================================================================
echo.

REM Verificar se o coletor existe
if not exist ecodash-collector.exe (
    echo Erro: ecodash-collector.exe nao encontrado!
    echo Baixe o arquivo do EcoDash Server.
    pause
    exit /b 1
)

REM Teste 1: Versão Pesada
echo [1/2] Testando VERSAO PESADA (ineficiente)...
echo.
ecodash-collector.exe heavy_project/data_processor_heavy.py
echo.
echo ✓ Teste da versão pesada concluído!
echo.
echo ============================================================================
echo.

REM Pausa entre testes
echo Aguardando 2 segundos antes do próximo teste...
timeout /t 2 /nobreak

echo.
REM Teste 2: Versão Otimizada
echo [2/2] Testando VERSAO OTIMIZADA (eficiente)...
echo.
ecodash-collector.exe optimized_project/data_processor_optimized.py
echo.
echo ✓ Teste da versão otimizada concluído!
echo.
echo ============================================================================
echo.
echo Testes concluídos! Verifique os resultados no dashboard EcoDash.
echo.
pause
