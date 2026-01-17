#!/bin/bash
# start.sh - Script para iniciar Nginx + Reflex

echo "Starting Nginx..."
nginx

echo "Starting Reflex on ports 3000 (frontend) and 8000 (backend)..."
# Unset PORT to prevent Reflex/FastAPI from binding to Railway's port 8080 automatically
# We want Nginx to handle 8080 and proxy to local 3000/8000
unset PORT
exec reflex run --env prod --frontend-port 3000 --backend-port 8000

