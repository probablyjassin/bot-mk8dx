FROM python:3.12-slim AS builder

# Install build dependencies
RUN apt-get update && apt-get install -y \
    wget \
    gnupg \
    git \
    gcc \
    g++ \
    python3-dev \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

# Install Cython and dependencies
COPY requirements.txt /app
RUN pip install --no-cache-dir -r requirements.txt
RUN pip install --no-cache-dir cython

# Copy source code
COPY . /app


# Compile Python files to .so
RUN python setup.py build_ext --inplace || \
    (echo "Compilation failed, checking directories..." && \
    find . -type d -name "database" -o -name "cogs" -o -name "utils" && \
    ls -la && exit 1)

# Remove original .py files (keep main.py)
RUN find . -type f -name "*.py" ! -name "main.py" ! -name "setup.py" -delete

# Runtime stage
FROM python:3.12-slim
LABEL org.opencontainers.image.source="https://github.com/probablyjassin/bot-mk8dx"

# Install minimal runtime dependencies
RUN apt-get update && apt-get install -y \
    libgomp1 \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

# Copy compiled extensions and dependencies
COPY --from=builder /usr/local/lib/python3.12/site-packages /usr/local/lib/python3.12/site-packages
COPY --from=builder /app /app

# Volumes for data
VOLUME /app/state
VOLUME /app/logs
VOLUME /app/backups

# Run with optimizations
ENV PYTHONUNBUFFERED=1
ENV PYTHONDONTWRITEBYTECODE=1
CMD ["python", "-OO", "-u", "main.py"]