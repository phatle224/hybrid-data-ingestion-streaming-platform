# Professional System Workflow Design Guide (Excalidraw Redesign Guide)

This document outlines the design principles, color palettes, tech icon integrations, and detailed structural content to help you redesign the `WORKFLOW.excalidraw` file from a simple text box diagram into a professional and visually rich enterprise architecture diagram.

---

## 1. Visual Design Principles

To ensure your architecture diagram looks clean, modern, and matches enterprise standards, follow these guidelines in Excalidraw:

### A. Typography & Content Hierarchy
- **Font Family**: Change all text elements from the default (Handwritten) style to **Sans-serif (Regular/Normal)**. Hand-drawn fonts should be avoided in technical diagrams to maintain a professional look.
- **Font Sizes**:
    - **Zone Titles (Group/Frame)**: `20px` or `24px` (Bold, Dark Gray `#495057`).
    - **Component/Technology Names**: `16px` (Bold, Black `#212529` or White if placed on dark backgrounds).
    - **Descriptions/Parameters**: `12px` (Normal, Gray `#6c757d` or lighter).
    - **Arrow Labels**: `11px` (Normal or Italic, Dark Gray).

### B. Grouping/Frame Bounding Boxes
- Use large rectangular boxes with **dashed strokes** and **rounded corners** to group different pipelines.
- **Background Fill**: Set the opacity to `5% - 10%` to add subtle depth without obscuring components.
    - *Example*: Online CDC pipeline uses a light blue background, Offline uses a light pink background, and Transformation uses a light orange background.

### C. Flow Connectors/Arrows
- Use **straight** or **orthogonal (elbow)** arrows instead of freeform curved lines.
- **Stroke Width**: `1px` or `1.5px`.
- **Stroke Style**:
    - `Solid`: Represents direct data streams (Data Ingestion, Writes, Materializations).
    - `Dashed`: Represents auxiliary check operations (Deduplication checks, API calls, Triggers).

---

## 2. System Color Palette & Technical Icons

Avoid using bright default colors (like pure red or pure green). Instead, use these calibrated brand color codes:

| Technology / Role | Proposed Hex Color | Recommended Icon |
| :--- | :--- | :--- |
| **PostgreSQL** (Source & Staging) | `#336791` (Slate Blue) | PostgreSQL Logo |
| **Debezium** (CDC Connector) | `#ff6b6b` (Soft Red) | Debezium Logo / Gear or Bolt icon |
| **Apache Kafka** (Event Broker) | `#231f20` (Dark Charcoal) | Apache Kafka Logo |
| **Python** (CDC & ETL Consumers)| `#3776ab` (Python Blue) | Python Logo |
| **React** (Portal Frontend) | `#61dafb` (Cyan) | React Logo |
| **FastAPI** (Portal Backend) | `#009688` (Teal) | FastAPI Logo |
| **dbt** (Dimensional Modeling) | `#ff6b4a` (Orange) | dbt Logo |
| **Docker** (Infrastructure) | `#2496ed` (Whale Blue) | Docker Logo |

### How to import professional SVG Icons into Excalidraw:
1. Visit free vector logo sites such as [Simple Icons](https://simpleicons.org/) or [Vector Logo Zone](https://www.vectorlogo.zone/).
2. Search for the respective logos (e.g., `PostgreSQL`, `Kafka`, `FastAPI`, `React`, `dbt`, `Docker`).
3. Download the **SVG** files.
4. **Drag and drop** the downloaded SVG files directly onto your Excalidraw canvas.
5. Resize the icons to a uniform dimension (recommended: **`48x48 px`** or **`60x60 px`**).

---

## 3. Detailed Component Attributes (Step-by-Step)

To make your diagram highly informative, replace short labels with the structured descriptions below:

### Zone 1: Online CDC Pipeline (Real-Time Ingestion)
*Outer Frame: Light blue dashed border, faint blue background.*

1. **PostgreSQL Icon (Source DB)**:
    - **Title**: `Production DB`
    - **Details**: `PostgreSQL (insuranceSale)`
    - **Role**: Stores real-time online transaction records.
2. **Debezium Icon (PostgreSQL Connector)**:
    - **Title**: `Debezium Connector`
    - **Details**: `WAL Logical Replication`
    - **Role**: Reads the Write-Ahead Log (WAL) asynchronously without locking tables.
3. **Apache Kafka Icon (Kafka Broker)**:
    - **Title**: `Kafka Topics`
    - **Details**: `source.public.* (Port 9092)`
    - **Role**: Buffers and queues events (CDC events) in a pub/sub model.
4. **Python Icon (CDC Consumer)**:
    - **Title**: `CDC Consumer`
    - **Details**: `Python Async Consumer`
    - **Role**: Consumes Kafka events $\rightarrow$ UPSERTs raw data into target Staging tables (`stgInsuranceContractObjectVehicle`, `stgInsuranceContractObjectTravel`, etc.).

---

### Zone 2: Offline Ingestion Pipeline (Batch Upload)
*Outer Frame: Light pink dashed border, faint pink background.*

1. **Excel/Document Icon**:
    - **Title**: `Partner Excel File`
    - **Details**: `Partner insurance contracts (Travel, Moto, Health, Medical...)`
2. **React Icon (Vite)**:
    - **Title**: `Portal Frontend`
    - **Details**: `React 18 + Vite (Port 3010)`
    - **Role**: Admin dashboard to log in and upload Excel reports.
3. **FastAPI Icon**:
    - **Title**: `Portal Backend`
    - **Details**: `FastAPI REST API (Port 3011)`
    - **Role**: Uses **Factory & Template Method Patterns** to dynamically parse Excel structures. Performs internal duplicate checks directly against PostgreSQL Staging tables.

---

### Zone 3: Staging Layer (Landing Area)
*Position: Physical convergence point of both pipelines.*

1. **Online Staging (PostgreSQL - Multiple Tables)**:
    - **Title**: `Online Staging Tables`
    - **Details**: `stgInsuranceContractObjectVehicle`, `stgInsuranceContractObjectTravel`...
    - **Role**: Holds raw data ingested via real-time CDC.
2. **Offline Staging (PostgreSQL - Single Table)**:
    - **Title**: `Offline Staging Table`
    - **Details**: `stgInsuranceContractObjectOffline`
    - **Role**: Holds raw data ingested via Excel uploads.

---

### Zone 4: ELT & Dimensional Modeling (dbt Transformation)
*Outer Frame: Light orange dashed border, faint orange background. This layer executes cross-channel deduplication.*

1. **Python Icon (Scheduler Daemon)**:
    - **Title**: `dbt Scheduler`
    - **Details**: `Incremental cron-job (Every 5 minutes)`
    - **Role**: Triggers periodic dbt execution.
2. **dbt Icon (Staging Models)**:
    - **Title**: `Staging Layer`
    - **Details**: `stg_contracts, stg_claims, stg_contract_objects_offline`
    - **Role**: Cleans data types and standardizes columns into English.
3. **dbt Icon (Intermediate Models - Cross-Deduplication)**:
    - **Title**: `Intermediate Layer`
    - **Details**: `int_contracts_joined, int_contracts_deduped`
    - **Role**:
        - `int_contracts_joined`: Performs a `UNION ALL` of Online and Offline sources.
        - `int_contracts_deduped`: Filters cross-channel duplicates using a 7 Business Keys match, implementing the **"Online Wins"** rule (`CASE WHEN source_type = 'online' THEN 1 ELSE 2 END ASC`).
4. **Dimension Tables Group - Light Green background**:
    - `dim_date`: Static calendar mapping 4,018 dates for time intelligence.
    - `dim_customer`: Buyer profile dimension.
    - `dim_insured_person`: Insured target profiles (incorporates decoded city codes and relationships).
    - `dim_product` + `dim_sales_channel`: Product details and sales channels.
5. **Fact Tables Group - Light Green background**:
    - `fct_contracts`: Contract transaction details at granular grain.
    - `fct_claims`: Insurance claim logs (processing duration, medical category).
6. **Data Marts Group - Deeper Green background**:
    - `dm_profiling_analysis`: Customer claims profiling (BI-ready).
    - `dm_contract_summary`: Overall sales performance and contract summary (BI-ready).

---

## 4. Recommended Layout Grid

To maintain a logical layout, design a **Left-to-Right Flow** combined with top-down source segregation:

```
[ ONLINE CDC CHANNEL ] ────────► [ ONLINE STAGING TABLES ] ───┐
                                                              ├─► [ UNION & DEDUP (dbt) ] ──► [ STAR SCHEMA ] ──► [ DATA MARTS ]
[ OFFLINE EXCEL CHANNEL ] ────► [ OFFLINE STAGING TABLE ] ────┘
```

- **Spacing**: Keep at least `60px` between components to allow room for connector labels and avoid visual clutter.
- **Docker Containerization**: You can draw a very light container boundary (Opacity 3%) around the entire diagram with a **Docker Icon** in the top-right corner to indicate that all services are fully containerized under Docker.
