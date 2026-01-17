#!/bin/bash
# start.sh - Script para iniciar Nginx + Reflex

# Iniciar Nginx em background
nginx

# Iniciar Reflex em foreground
reflex run --env prod --frontend-port 3001 --backend-port 8001
