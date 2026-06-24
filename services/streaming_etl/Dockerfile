FROM python:3.11-slim

WORKDIR /app

RUN apt-get update && apt-get install -y --no-install-recommends gcc && rm -rf /var/lib/apt/lists/*

# Install shared package
COPY shared/ /tmp/shared/
RUN pip install --no-cache-dir /tmp/shared/ && rm -rf /tmp/shared/

# Install service-specific dependencies
COPY streaming_etl/requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy service source (includes configs/, models/, processors/, services/)
COPY streaming_etl/src/ .

RUN mkdir -p /app/logs

HEALTHCHECK --interval=60s --timeout=10s --start-period=30s --retries=3 \
    CMD python -c "import sys; sys.exit(0)"

CMD ["python", "-c", "import time, sys; print('Streaming ETL consumer replaced by dbt. Container kept alive for running tools.'); sys.stdout.flush(); time.sleep(99999999)"]
