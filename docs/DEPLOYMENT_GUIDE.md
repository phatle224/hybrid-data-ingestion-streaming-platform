# Deployment Guide

This guide provides step-by-step instructions to spin up the entire infrastructure of the **Hybrid Data Ingestion & Streaming ETL Platform** locally using Docker Compose.

---

## 1. Environment Preparation
1. Copy the environment configuration from the template file:
   ```powershell
   cp .env.example .env
   ```
2. Initialize a shared Docker network for the entire project:
   ```powershell
   docker network create cdc-network
   ```

---

## 2. Infrastructure Launch

Launch the infrastructure components in the following order to ensure smooth connectivity:

### Step 2.1: Start the Databases (PostgreSQL)
Run both the source database (Production DB) and the target database (Staging/Reporting DB):
```powershell
docker-compose -f docker-compose.db.yml up -d
```
*   **Production DB** port: `5432`
*   **Staging/Warehouse DB** port: `5433`

### Step 2.2: Start Kafka (Message Queue System)
```powershell
docker-compose -f docker-compose.kafka.yml up -d
```
*Wait about 10-15 seconds for the Kafka Broker to fully start.*

### Step 2.3: Start Debezium Connect (CDC Monitoring)
```powershell
docker-compose -f docker-compose.debezium.yml up -d
```
*Wait about 20-30 seconds for the Debezium Connect REST API to become ready.*

---

## 3. Register Debezium Connector

Register the connector to start capturing data changes (CDC) from the Production DB and streaming them into Kafka:

```powershell
# Using PowerShell
Invoke-RestMethod -Uri "http://localhost:8083/connectors" `
  -Method Post `
  -ContentType "application/json" `
  -Body (Get-Content configs\register-source-connector.json -Raw)
```

**Check operational status (should return a status of `RUNNING`):**
```powershell
Invoke-RestMethod -Uri "http://localhost:8083/connectors/postgresql-source-connector/status"
```

---

## 4. Launch Streaming Consumer & Scheduler

### Step 4.1: Start the CDC Consumer
Sync database change events from Kafka to the Staging Database:
```powershell
docker-compose -f docker-compose.consumer.yml up -d --build
```

### Step 4.2: Start the dbt Transformation Scheduler
The scheduler background daemon runs dbt transformations to convert data into the Star Schema:
```powershell
docker-compose -f docker-compose.scheduler.yml up -d --build
```

### Step 4.3: Start the Mock Data Generator
Automatically insert and simulate transactions on the source database (for demonstration purposes):
```powershell
docker-compose -f docker-compose.generator.yml up -d --build
```

---

## 5. Start the Offline Ingestion Portal (UI)

Start the management UI and Excel upload portal:
```powershell
docker-compose -f docker-compose.portal.yml up -d --build
```

*   **Portal Frontend**: Access at [http://localhost:3000](http://localhost:3000)
*   **Portal Backend API**: Access at [http://localhost:8000](http://localhost:8000)
*   **Kafka UI**: Access at [http://localhost:9999](http://localhost:9999) (monitors Kafka Topics)

---

## 6. Verification & Data Checking
You can connect to the PostgreSQL Staging/Warehouse database on port `5433` (User: `postgres`, Password: `password`) to check the reporting tables:
- Check Dimension tables: `select count(*) from warehouse.dim_customer;`
- Check Fact tables: `select count(*) from warehouse.fct_contracts;`
- Check Data Marts: `select count(*) from mart.dm_profiling_analysis;`
