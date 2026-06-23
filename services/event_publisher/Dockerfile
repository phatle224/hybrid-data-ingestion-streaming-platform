FROM python:3.11-slim

WORKDIR /app

# Install dependencies (standalone — no shared package needed)
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy service source
COPY src/event_publisher.py .

CMD ["python", "-u", "event_publisher.py"]
