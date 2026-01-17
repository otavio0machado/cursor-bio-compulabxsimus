#!/bin/bash
# start.sh - Script para iniciar Nginx + Reflex

echo "Starting Nginx..."
nginx

echo "Starting Reflex on ports 3000 (frontend) and 8000 (backend)..."
exec reflex run --env prod --frontend-port 3000 --backend-port 8000
