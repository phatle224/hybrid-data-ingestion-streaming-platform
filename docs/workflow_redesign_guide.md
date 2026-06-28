# Hướng Dẫn Thiết Kế Workflow Hệ Thống Chuyên Nghiệp (Excalidraw Redesign Guide)

Tài liệu này cung cấp các nguyên tắc thiết kế, bảng màu, cách tích hợp icon công nghệ và nội dung chi tiết để bạn có thể tự thiết kế lại file `WORKFLOW.excalidraw` từ dạng **hộp chữ đơn giản (Hình 1)** thành một **sơ đồ kiến trúc doanh nghiệp chuẩn mực và trực quan (như ví dụ ở Hình 2)**.

---

## 🎨 1. Nguyên Tắc Thiết Kế Trực Quan (Visual Design Principles)

Để sơ đồ trông sạch sẽ, hiện đại và chuẩn "Enterprise Architecture", hãy tuân thủ các quy tắc sau trong Excalidraw:

### A. Font Chữ & Phân Cấp Nội Dung (Typography & Hierarchy)
*   **Font Family**: Đổi toàn bộ text từ dạng mặc định (Handwritten) sang **Sans-serif (Regular/Normal)**. Sơ đồ kỹ thuật tuyệt đối không dùng nét chữ viết tay để đảm bảo tính chuyên nghiệp.
*   **Kích thước chữ**:
    *   **Tiêu đề phân vùng (Group/Frame)**: `20px` hoặc `24px` (Bold, màu xám đậm `#495057`).
    *   **Tên Component/Công nghệ**: `16px` (Bold, màu đen `#212529` hoặc trắng nếu nền tối).
    *   **Mô tả chi tiết/Tham số**: `12px` (Normal, màu xám `#6c757d` hoặc nhạt hơn).
    *   **Nhãn mũi tên luồng (Arrow Label)**: `11px` (Normal hoặc Italic, màu xám đậm).

### B. Cấu Trúc Khung Phân Vùng (Bounding Boxes / Frames)
*   Sử dụng các khung chữ nhật lớn với **nét đứt (dashed stroke)** và **góc bo tròn (rounded corners)** để gom nhóm các pipeline.
*   **Màu nền của Khung**: Đặt độ mờ (Opacity) khoảng `5% - 10%` để tạo chiều sâu mà không làm mờ các component bên trong.
    *   *Ví dụ*: Phân vùng Online dùng nền màu xanh lam nhạt, Phân vùng Offline dùng nền hồng nhạt, Phân vùng Transformation dùng nền cam nhạt.

### C. Mũi Tên Chỉ Luồng (Connectors)
*   Sử dụng mũi tên **thẳng (straight)** hoặc **vuông góc (elbow/orthogonal)** thay vì mũi tên cong tự do.
*   **Độ dày nét**: `1px` hoặc `1.5px`.
*   **Kiểu nét**:
    *   `Nét liền (Solid)`: Thể hiện dòng chảy dữ liệu trực tiếp (Data Ingestion, Write, Materialize).
    *   `Nét đứt (Dashed)`: Thể hiện các hoạt động đọc/kiểm tra phụ trợ (Deduplication Check, API Call, Trigger).

---

## 💾 2. Bảng Màu Hệ Thống & Bộ Icon Kỹ Thuật (Color Palette & SVGs)

Tránh sử dụng các màu mặc định chói mắt (như đỏ nguyên bản, xanh lá nguyên bản). Hãy dùng các mã màu thương hiệu đã được căn chỉnh tinh tế sau đây:

| Công Nghệ / Vai Trò | Mã Màu Hex gợi ý | Icon đề xuất |
| :--- | :--- | :--- |
| **PostgreSQL** (Source & Staging) | `#336791` (Slate Blue) | Logo PostgreSQL (Con voi xanh) |
| **Debezium** (CDC Connector) | `#ff6b6b` (Soft Red) | Logo Debezium hoặc Icon bánh răng/tia sét |
| **Apache Kafka** (Event Broker) | `#231f20` (Dark Charcoal) | Logo Apache Kafka |
| **Python** (CDC & ETL Consumers)| `#3776ab` (Python Blue) | Logo Python |
| **React** (Portal Frontend) | `#61dafb` (Cyan) | Logo React (Vòng xoáy nguyên tử) |
| **FastAPI** (Portal Backend) | `#009688` (Teal) | Logo FastAPI (Tia sét màu xanh teal) |
| **dbt** (Dimensional Modeling) | `#ff6b4a` (Orange) | Logo dbt (Hình khối cam) |
| **Docker** (Infrastructure) | `#2496ed` (Whale Blue) | Logo Docker (Chú cá voi xanh) |

### 🛠️ Cách đưa Icon SVG chuyên nghiệp vào Excalidraw:
1.  Truy cập các trang web logo vector miễn phí như [Simple Icons](https://simpleicons.org/) hoặc [Vector Logo Zone](https://www.vectorlogo.zone/).
2.  Tìm kiếm logo tương ứng (ví dụ: `PostgreSQL`, `Kafka`, `FastAPI`, `React`, `dbt`, `Docker`).
3.  Tải file **SVG** về máy tính của bạn.
4.  **Kéo thả trực tiếp** file SVG vừa tải vào khung làm việc của Excalidraw. 
5.  Co giãn icon về kích thước chuẩn (khuyên dùng khoảng **`48x48 px`** hoặc **`60x60 px`**) để tạo sự đồng bộ.

---

## 📑 3. Nội Dung Chi Tiết Từng Thành Phần (Step-by-Step Component Details)

Để sơ đồ của bạn không chỉ đẹp mà còn giàu thông tin (như hình 2), hãy thay thế các text box ngắn cũn bằng cấu trúc mô tả chi tiết dưới đây:

### 🌐 Phân Vùng 1: Online CDC Pipeline (Kênh Trực Tuyến)
*Khung bao ngoài: Nét đứt màu xanh dương nhạt. Nền xanh mờ.*

1.  **Icon PostgreSQL (Source DB)**:
    *   **Tiêu đề**: `Production DB`
    *   **Chi tiết**: `PostgreSQL (insuranceSale)`
    *   **Nhiệm vụ**: Lưu trữ giao dịch trực tuyến thời gian thực.
2.  **Icon Debezium (PostgreSQL Connector)**:
    *   **Tiêu đề**: `Debezium Connector`
    *   **Chi tiết**: `WAL Logical Replication`
    *   **Nhiệm vụ**: Đọc Write-Ahead Log (WAL) không gây khóa bảng.
3.  **Icon Apache Kafka (Kafka Broker)**:
    *   **Tiêu đề**: `Kafka Topics`
    *   **Chi tiết**: `source.public.* (Port 9092)`
    *   **Nhiệm vụ**: Lưu trữ hàng đợi sự kiện (CDC Events) dưới dạng pub/sub.
4.  **Icon Python (CDC Consumer)**:
    *   **Tiêu đề**: `CDC Consumer`
    *   **Chi tiết**: `Python Async Consumer`
    *   **Nhiệm vụ**: Lắng nghe Kafka $\rightarrow$ UPSERT dữ liệu thô vào các bảng Staging riêng biệt (`stgInsuranceContractObjectVehicle`, `stgInsuranceContractObjectTravel`, etc.).

---

### 📥 Phân Vùng 2: Offline Ingestion Pipeline (Kênh Ngoại Tuyến)
*Khung bao ngoài: Nét đứt màu hồng nhạt. Nền hồng mờ.*

1.  **Icon Excel / Document**:
    *   **Tiêu đề**: `Partner Excel File`
    *   **Chi tiết**: `Hợp đồng bảo hiểm đối tác (Travel, Moto, Health, Medical...)`
2.  **Icon React (Vite)**:
    *   **Tiêu đề**: `Portal Frontend`
    *   **Chi tiết**: `React 18 + Vite (Port 3010)`
    *   **Nhiệm vụ**: UI cho quản trị viên đăng nhập và tải lên file Excel.
3.  **Icon FastAPI**:
    *   **Tiêu đề**: `Portal Backend`
    *   **Chi tiết**: `FastAPI REST API (Port 3011)`
    *   **Nhiệm vụ**: Áp dụng **Factory & Template Method Patterns** để phân loại và xử lý file Excel động. Thực hiện check trùng lặp nội bộ (Deduplication Check) trực tiếp trên bảng `stgInsuranceContractObjectOffline`.

---

### 🗄️ Phân Vùng 3: Staging Layer (Vùng Đệm)
*Vị trí: Điểm hội tụ vật lý của luồng dữ liệu.*

1.  **Bảng Staging Online (PostgreSQL - Multiple Tables)**:
    *   **Tiêu đề**: `Online Staging Tables`
    *   **Chi tiết**: `stgInsuranceContractObjectVehicle`, `stgInsuranceContractObjectTravel`...
    *   **Nhiệm vụ**: Lưu trữ dữ liệu thô trực tiếp từ CDC.
2.  **Bảng Staging Offline (PostgreSQL - Single Table)**:
    *   **Tiêu đề**: `Offline Staging Table`
    *   **Chi tiết**: `stgInsuranceContractObjectOffline`
    *   **Nhiệm vụ**: Lưu trữ dữ liệu thô tải lên từ file Excel.

---

### 🏗️ Phân Vùng 4: ELT & Dimensional Modeling (Tầng Biến Đổi dbt)
*Khung bao ngoài: Nét đứt màu cam nhạt. Nền cam mờ. Đây chính là nơi xử lý loại bỏ trùng lặp chéo giữa Online và Offline.*

1.  **Icon Python (Scheduler Daemon)**:
    *   **Tiêu đề**: `dbt Scheduler`
    *   **Chi tiết**: `Incremental cron-job (Mỗi 5 phút)`
    *   **Nhiệm vụ**: Kích hoạt dbt biến đổi dữ liệu gia tăng.
2.  **Icon dbt (Staging Models)**:
    *   **Tiêu đề**: `Staging Layer`
    *   **Chi tiết**: `stg_contracts, stg_claims, stg_contract_objects_offline`
    *   **Nhiệm vụ**: Clean kiểu dữ liệu, chuẩn hóa cột sang tiếng Anh.
3.  **Icon dbt (Intermediate Models - Khử trùng chéo)**:
    *   **Tiêu đề**: `Intermediate Layer`
    *   **Chi tiết**: `int_contracts_joined, int_contracts_deduped`
    *   **Nhiệm vụ**: 
        *   `int_contracts_joined`: `UNION ALL` dữ liệu Online và Offline.
        *   `int_contracts_deduped`: Khử trùng chéo giữa 2 kênh qua 7 Business Keys bằng phép `ROW_NUMBER()` với thứ tự ưu tiên **"Online Wins"** (`CASE WHEN source_type = 'online' THEN 1 ELSE 2 END ASC`).
4.  **Nhóm các Bảng Chiều (Dimensions) - Nền màu xanh lá nhạt**:
    *   `dim_date`: Khởi tạo tĩnh 4,018 dòng phân tích thời gian.
    *   `dim_customer`: Thông tin người mua bảo hiểm.
    *   `dim_insured_person`: Thông tin người được bảo hiểm (chứa logic giải mã tỉnh thành/quan hệ).
    *   `dim_product` + `dim_sales_channel`: Gói sản phẩm và kênh phân phối.
5.  **Nhóm các Bảng Sự Kiện (Facts) - Nền màu xanh lá nhạt**:
    *   `fct_contracts`: Lưu trữ chi tiết giao dịch hợp đồng theo grain hạt mịn.
    *   `fct_claims`: Các sự kiện yêu cầu bồi thường (chẩn đoán y khoa, thời gian xử lý).
6.  **Nhóm Tầng Báo Cáo (Data Marts) - Nền màu xanh lá nhạt đậm**:
    *   `dm_profiling_analysis`: Claim Profiling (Sẵn sàng cho BI/Tableau/PowerBI).
    *   `dm_contract_summary`: Doanh thu và số lượng hợp đồng (Sẵn sàng cho BI).

---

## 📐 4. Gợi Ý Bố Cục Tổng Thế (Recommended Layout Grid)

Để sơ đồ của bạn gọn gàng như Hình 2, hãy áp dụng bố cục **từ trái qua phải (Left-to-Right Flow)** kết hợp với phân lớp **từ trên xuống dưới**:

```
[ KÊNH ONLINE CDC ] ────────► [ ONLINE STAGING TABLES ] ───┐
                                                            ├─► [ UNION & DEDUP (dbt) ] ──► [ STAR SCHEMA ] ──► [ DATA MARTS ]
[ KÊNH OFFLINE EXCEL ] ──────► [ OFFLINE STAGING TABLE ] ──┘
```

*   **Tỷ lệ khoảng cách**: Giữ khoảng cách giữa các component tối thiểu `60px` để vẽ mũi tên luồng và nhãn giải thích không bị chồng chéo lên nhau.
*   **Docker Containerization**: Bạn có thể vẽ thêm một đường bao ngoài mờ nhất (Opacity 3%) bao phủ toàn bộ sơ đồ với **Icon Docker** ở góc trên cùng bên phải để thể hiện toàn bộ hệ thống được đóng gói bằng Docker Containers, mang lại cái nhìn cực kỳ trực quan và cao cấp.
