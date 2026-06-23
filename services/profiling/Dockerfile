FROM python:3.11-slim

WORKDIR /app

RUN apt-get update && apt-get install -y --no-install-recommends gcc && rm -rf /var/lib/apt/lists/*

# Install shared package
COPY shared/ /tmp/shared/
RUN pip install --no-cache-dir /tmp/shared/ && rm -rf /tmp/shared/

# Install service-specific dependencies
COPY profiling/requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy service source
COPY profiling/src/ .

RUN mkdir -p /app/logs

CMD ["python", "-u", "profiling_consumer.py"]
