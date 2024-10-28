FROM --platform=$TARGETPLATFORM python:3.9-slim

# Install Chrome and dependencies for both architectures
RUN apt-get update && apt-get install -y \
    wget \
    gnupg \
    chromium \
    chromium-driver \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

COPY requirements.txt /app

RUN pip install --no-cache-dir -r requirements.txt

COPY . /app

# Add volume for data
VOLUME /app/data

# Define environment variables
ENV DISCORD_TOKEN = ""
ENV MONGO_URI = ""
ENV LOUNGE_DB = ""
ENV GUILD_IDS = ''
ENV LOG_CHANNEL_ID = ''
ENV REGISTER_CHANNEL_ID = ''

CMD ["python", "-u", "main.py"]
