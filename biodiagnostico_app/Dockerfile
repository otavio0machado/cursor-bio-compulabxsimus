# Dockerfile simples para Reflex App
FROM python:3.11-slim

WORKDIR /app

# Instalar dependências do sistema
RUN apt-get update && apt-get install -y \
    nodejs \
    npm \
    git \
    unzip \
    curl \
    ca-certificates \
    && rm -rf /var/lib/apt/lists/*

# Copiar código
COPY . .

# Instalar dependências Python
RUN pip install --no-cache-dir -r requirements.txt

# Inicializar Reflex
RUN reflex init

# Criar diretório para uploads
RUN mkdir -p /app/uploaded_files

# Expor porta única
EXPOSE 8080

# Rodar Reflex diretamente na porta 8080
CMD ["reflex", "run", "--env", "prod", "--frontend-port", "8080", "--backend-port", "8000"]
