# Dockerfile para Reflex + Nginx
FROM python:3.11-slim

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

# Converter line endings do arquivo start.sh (Windows CRLF -> Unix LF)
RUN apt-get update && apt-get install -y dos2unix && rm -rf /var/lib/apt/lists/*
RUN dos2unix start.sh
RUN chmod +x start.sh

RUN mkdir -p /app/uploaded_files

EXPOSE 8080

CMD ["./start.sh"]
