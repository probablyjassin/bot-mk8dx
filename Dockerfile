FROM python:3.12-slim

# Metadata
LABEL org.opencontainers.image.source="https://github.com/probablyjassin/bot-mk8dx"

# Setup project and install dependencies
WORKDIR /app

COPY requirements.txt /app

# Use BuildKit cache mount for pip packages
# Cache is used during build but not kept in final image
RUN --mount=type=cache,target=/root/.cache/pip \
    pip install -r requirements.txt

COPY . /app

# Add volumes for data
VOLUME /app/state
VOLUME /app/logs
VOLUME /app/backups

CMD ["python", "-u", "main.py"]
