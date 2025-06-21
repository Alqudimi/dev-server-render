
# Use official Python image as base
FROM python:3.9-slim

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1
ENV DEBIAN_FRONTEND noninteractive

# Install system dependencies
RUN apt-get update && apt-get install -y \
    build-essential \
    curl \
    git \
    nginx \
    wget \
    unzip \
    # Language specific tools
    openjdk-11-jdk \
    nodejs \
    npm \
    ruby \
    golang \
    rustc \
    cargo \
    php \
    && rm -rf /var/lib/apt/lists/*

# Install language version managers
RUN curl -fsSL https://raw.githubusercontent.com/pyenv/pyenv-installer/master/bin/pyenv-installer | bash && \
    curl -o- https://raw.githubusercontent.com/nvm-sh/nvm/v0.39.1/install.sh | bash

# Set up workspace
RUN mkdir -p /app/{api,projects,scripts,configs,logs}
WORKDIR /app/api

# Copy API files
COPY ./api/src/requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy all other files
COPY . .

# Set up scripts
RUN chmod +x /app/scripts/*.sh && \
    /app/scripts/setup_environment.sh

# Expose ports
EXPOSE 80 443 8000

# Start services
CMD ["sh", "-c", "nginx && uvicorn main:app --host 0.0.0.0 --port 8000"]
