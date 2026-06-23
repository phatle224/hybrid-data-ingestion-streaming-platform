FROM python:3.11-slim

WORKDIR /app

# Install shared package
COPY shared/ /tmp/shared/
RUN pip install --no-cache-dir /tmp/shared/ && rm -rf /tmp/shared/

# Install service-specific dependencies
COPY cdc_consumer/requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy service source
COPY cdc_consumer/src/ .

RUN mkdir -p /app/logs

CMD ["python", "-u", "cdc_consumer.py"]
