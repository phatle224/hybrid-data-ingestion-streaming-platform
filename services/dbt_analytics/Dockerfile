FROM python:3.10-slim

# Install system dependencies needed for compilation (e.g. pg_config for psycopg2 if compiled)
RUN apt-get update && apt-get install -y --no-install-recommends \
    git \
    libpq-dev \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

# Set working directory inside container
WORKDIR /usr/app

# Install dbt-postgres directly
RUN pip install --no-cache-dir dbt-postgres

# Copy dbt project files and the scheduler script
COPY services/dbt_analytics/ /usr/app/dbt_analytics/
COPY scripts/dbt_scheduler.py /usr/app/dbt_scheduler.py

# Set working directory to the dbt analytics folder so profiles-dir context resolves correctly
WORKDIR /usr/app/dbt_analytics

# Environmental configurations for the scheduler
ENV SCHEDULER_INTERVAL=300
ENV DBT_DIR=/usr/app/dbt_analytics
ENV LOG_FILE=/usr/app/dbt_analytics/logs/dbt_scheduler.log

# Command to run the scheduler
CMD ["python", "-u", "/usr/app/dbt_scheduler.py"]
