#!/bin/bash

echo "Starting Container"

# Debug: Verificar estrutura do build ANTES de iniciar serviços
echo "=== Debug: Conteúdo de build/client ==="
if [ -d "/app/.web/build/client" ]; then
    ls -F /app/.web/build/client
    echo "--- Verificando assets críticos ---"
    
    # Verificar se existe pelo menos um arquivo de global styles
    GLOBAL_CSS=$(find /app/.web/build/client/assets -name "__reflex_global_styles*.css" 2>/dev/null | head -1)
    if [ -n "$GLOBAL_CSS" ]; then
        echo "✓ Global styles encontrado: $(basename $GLOBAL_CSS)"
    else
        echo "⚠ AVISO: Global styles não encontrado!"
    fi
    
    # Verificar manifest
    MANIFEST=$(find /app/.web/build/client/assets -name "manifest*.js" 2>/dev/null | head -1)
    if [ -n "$MANIFEST" ]; then
        echo "✓ Manifest encontrado: $(basename $MANIFEST)"
    else
        echo "⚠ AVISO: Manifest não encontrado!"
    fi
    
    # Contar total de assets
    ASSET_COUNT=$(ls -1 /app/.web/build/client/assets 2>/dev/null | wc -l)
    echo "✓ Total de assets: $ASSET_COUNT arquivos"
else
    echo "ERRO CRÍTICO: Diretório /app/.web/build/client NÃO ENCONTRADO!"
    exit 1
fi
echo "======================================" 

echo "Aguardando Reflex iniciar em background..."

# Iniciar Reflex em background (apenas backend)
reflex run --env prod --backend-only --backend-port 8000 &
REFLEX_PID=$!

# Aguardar Backend estar pronto (máximo 60 segundos)
echo "Aguardando backend (porta 8000)..."
for i in {1..60}; do
    if curl -s http://127.0.0.1:8000/ping > /dev/null 2>&1; then
        echo "Backend pronto!"
        break
    fi
    sleep 1
done

echo "Iniciando Nginx..."
nginx -g "daemon off;" &
NGINX_PID=$!

# Manter o container rodando
wait $REFLEX_PID

