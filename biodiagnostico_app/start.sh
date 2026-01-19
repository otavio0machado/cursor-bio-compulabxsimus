#!/bin/bash

echo "Aguardando Reflex iniciar em background..."

# Iniciar Reflex em background
reflex run --env prod --frontend-port 3000 --backend-port 8000 &
REFLEX_PID=$!

# Aguardar Reflex estar pronto (máximo 300 segundos)
echo "Aguardando frontend (porta 3000)..."
for i in {1..300}; do
    if curl -s http://127.0.0.1:3000 > /dev/null 2>&1; then
        echo "Frontend pronto!"
        break
    fi
    sleep 1
done

echo "Iniciando Nginx..."
nginx -g "daemon off;" &
NGINX_PID=$!

# Manter o container rodando
wait $REFLEX_PID
