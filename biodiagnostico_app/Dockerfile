# Dockerfile para Reflex + Nginx
# Build: 2026-01-22T18:33:00Z - Force rebuild with nginx cache fix
FROM python:3.11-slim

# Cache bust to force fresh build
ARG CACHEBUST=1

WORKDIR /app

# Instalar dependências
RUN apt-get update && apt-get install -y \
    nodejs \
    npm \
    git \
    unzip \
    curl \
    ca-certificates \
    nginx \
    && rm -rf /var/lib/apt/lists/*

COPY . .

RUN pip install --no-cache-dir -r requirements.txt

# Aumentar limite de memória do Node para evitar crash durante o build do frontend
ENV NODE_OPTIONS="--max-old-space-size=4096"

RUN rm -rf .web/build .web/dev-server
RUN reflex init

# Pré-build do frontend com loglevel debug
RUN reflex export --frontend-only --no-zip --loglevel debug

COPY nginx.conf /etc/nginx/nginx.conf

RUN chmod +x start.sh

RUN mkdir -p /app/uploaded_files

EXPOSE 8080

CMD ["./start.sh"]
