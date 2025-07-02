# Simple Python Flask Application Dockerfile
FROM python:3.11.4-slim

# Install build dependencies for packages like psutil
RUN apt-get update && apt-get install -y \
    gcc \
    python3-dev \
    && rm -rf /var/lib/apt/lists/*

# Set working directory
WORKDIR /

# Copy application files
COPY requirements.txt /
RUN pip install --no-cache-dir -r requirements.txt

COPY main.py /
COPY gunicorn.conf.py /
COPY src/ /src/
COPY bbs_core_simple.py /bbs_core.py

# Run the Python service
ENTRYPOINT ["python", "main.py"]
