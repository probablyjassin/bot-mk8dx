FROM python:3.10-slim

# Metadata
LABEL org.opencontainers.image.source = "https://github.com/probablyjassin/bot-mk8dx"

# Install base dependencies
RUN apt-get update && apt-get install -y \
    wget \
    gnupg \
    chromium \
    chromium-driver \
    git \
    && rm -rf /var/lib/apt/lists/*

# Setup project and install dependencies
WORKDIR /app

COPY requirements.txt /app

RUN pip install --no-cache-dir -r requirements.txt

COPY . /app

# Add volume for data
VOLUME /app/data

CMD ["python", "-u", "main.py"]
