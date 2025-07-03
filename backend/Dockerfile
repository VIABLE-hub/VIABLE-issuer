# Production-Ready Python Flask Application Dockerfile with Rust for BBS+ Core
FROM python:3.11.4-slim

# Install system dependencies for Rust, BBS+ core, and general app requirements
RUN apt-get update && apt-get install -y \
    gcc \
    python3-dev \
    curl \
    build-essential \
    pkg-config \
    libssl-dev \
    && rm -rf /var/lib/apt/lists/*

# Install Rust (required for BBS+ core compilation)
RUN curl --proto '=https' --tlsv1.2 -sSf https://sh.rustup.rs | sh -s -- -y
ENV PATH="/root/.cargo/bin:${PATH}"

# Set working directory
WORKDIR /app

# Copy requirements and install Python dependencies
COPY requirements.txt /app/
RUN pip install --no-cache-dir -r requirements.txt

# Copy BBS+ core source code first (for compilation)
COPY bbs-core/ /app/bbs-core/

# Compile BBS+ core library with proper cleanup
WORKDIR /app/bbs-core
RUN cargo clean && \
    cargo build --release && \
    rm -rf python/*.py python/*.so python/*.dylib 2>/dev/null || true && \
    cargo run --bin uniffi-bindgen --features="uniffi/cli" generate --library target/release/libbbs_core.so --language python --out-dir python/

# Copy the compiled library to the expected location
RUN cp target/release/libbbs_core.so /app/libbbs_core.so

# Return to app directory
WORKDIR /app

# Copy application files
COPY main.py /app/
COPY gunicorn.conf.py /app/
COPY src/ /app/src/
COPY bbs_core_simple.py /app/
COPY bbs_core.py /app/

# Create necessary directories and set permissions
RUN mkdir -p /app/data /app/static /app/logs \
    && chmod +x /app/libbbs_core.so \
    && chmod +x /app/bbs-core/target/release/libbbs_core.so 2>/dev/null || true \
    && chmod +x /app/bbs-core/python/libbbs_core.dylib 2>/dev/null || true

# Set Python path to include BBS+ core
ENV PYTHONPATH=/app:/app/bbs-core/python:/app/src
ENV BBS_CORE_PATH=/app/bbs-core/python
ENV LD_LIBRARY_PATH=/app:/app/bbs-core/target/release:${LD_LIBRARY_PATH}

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD curl -f http://localhost:8080/health || exit 1

# Expose port
EXPOSE 8080

# Run the Python service
ENTRYPOINT ["python", "main.py"]
