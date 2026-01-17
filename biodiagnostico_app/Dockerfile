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

RUN reflex init

COPY nginx.conf /etc/nginx/nginx.conf

RUN chmod +x start.sh

RUN mkdir -p /app/uploaded_files

EXPOSE 8080

CMD ["./start.sh"]
