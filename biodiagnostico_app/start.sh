#!/bin/bash

echo "Aguardando Reflex iniciar em background..."

# Iniciar Reflex em background
# Iniciar Reflex em background (apenas backend)
reflex run --env prod --backend-only --backend-port 8000 &
REFLEX_PID=$!

# Debug: Listar arquivos gerados
echo "=== Debug: Conteúdo de .web ==="
ls -la /app/.web || echo ".web não encontrado"
ls -la /app/.web/_static || echo ".web/_static não encontrado"
echo "=============================="

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
