FROM python:3.12-slim

# Metadata
LABEL org.opencontainers.image.source="https://github.com/probablyjassin/bot-mk8dx"

# Install base dependencies
RUN apt-get update && apt-get install -y \
    wget \
    gnupg \
    git \
    && rm -rf /var/lib/apt/lists/*

# Setup project and install dependencies
WORKDIR /app

COPY requirements.txt /app

RUN pip install --no-cache-dir -r requirements.txt
#RUN playwright install-deps
#RUN playwright install chromium

COPY . /app

# Add volumes for data
VOLUME /app/state
VOLUME /app/logs
VOLUME /app/backups

CMD ["python", "-u", "main.py"]
