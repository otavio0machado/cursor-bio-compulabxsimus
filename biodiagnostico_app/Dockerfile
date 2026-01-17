# Dockerfile for Reflex App with Nginx (100MB upload support)
FROM python:3.11-slim

WORKDIR /app

# Install system dependencies including nginx and curl (required for reflex init)
RUN apt-get update && apt-get install -y \
    nodejs \
    npm \
    git \
    unzip \
    nginx \
    curl \
    ca-certificates \
    && rm -rf /var/lib/apt/lists/*

# Copy local code to the container
COPY . .

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Initialize Reflex (downloads frontend packages)
RUN reflex init

# Copy nginx config
COPY nginx.conf /etc/nginx/nginx.conf

# Make start script executable
RUN chmod +x start.sh

# Create uploaded_files directory
RUN mkdir -p /app/uploaded_files

# Expose ports
EXPOSE 3000
EXPOSE 8000

# Command to run the application
CMD ["./start.sh"]

