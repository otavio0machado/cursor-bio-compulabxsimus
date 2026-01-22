#!/bin/bash

echo "Aguardando Reflex iniciar em background..."

# Iniciar Reflex em background
# Iniciar Reflex em background (apenas backend)
# Iniciar Reflex em background (apenas backend)
reflex run --env prod --backend-only --backend-port 8000 &
REFLEX_PID=$!

# Debug: Verificar estrutura do build (importante para assets)
echo "=== Debug: Verificando estrutura do build em /app/.web/build/client ==="
if [ -d "/app/.web/build/client" ]; then
    echo "Diretório do build encontrado."
    ls -F /app/.web/build/client
    echo "--- Conteúdo de assets/ ---"
    ls -F /app/.web/build/client/assets | head -n 100
else
    echo "ERRO: Diretório /app/.web/build/client NÃO ENCONTRADO!"
fi
echo "======================================"

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
