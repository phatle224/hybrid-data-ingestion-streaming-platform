# Hướng Dẫn Chuyển Đổi Dự Án Thành Portfolio Cá Nhân Đưa Vào CV

Tài liệu này hướng dẫn cách chuyển đổi hệ thống **Hybrid Data Ingestion & Streaming ETL** từ một dự án nội bộ của công ty thành một dự án cá nhân ấn tượng trên GitHub và CV của bạn, đồng thời giải đáp chi tiết các câu hỏi về mặt kiến trúc hệ thống.

---

## Part 1: Câu Hỏi Nghiệp Vụ & Kiến Trúc

### Câu hỏi 1: Hiện tại không truy cập được database source nữa thì làm sao?
**Giải pháp:** Hoàn toàn có thể và rất nên dựng một **Local Source Database** chạy bằng Docker để biến dự án thành một hệ thống khép kín, có thể chạy demo (self-contained) ngay trên máy của bạn hoặc nhà tuyển dụng.
*   **Cách làm:**
    1. Thêm một service MySQL (đóng vai trò là Production DB) vào hệ thống Docker Compose.
    2. Viết một script Python đơn giản (sử dụng thư viện `Faker`) đặt tên là `seed_data.py`. Script này sẽ liên tục giả lập hành vi người dùng bằng cách chèn (INSERT), cập nhật (UPDATE) ngẫu nhiên các hợp đồng và claims vào Local Source DB này.
    3. Cấu hình container Local MySQL này bật sẵn **MySQL Binlog** để Debezium Connect có thể lắng nghe và stream dữ liệu sang Kafka giống y hệt như môi trường thật của công ty.
*   *Lợi ích:* Dự án của bạn sẽ có một nút bấm khởi động duy nhất (`docker compose up`) và tự động chạy demo luồng dữ liệu nhảy real-time từ Source $\rightarrow$ Kafka $\rightarrow$ Staging $\rightarrow$ Reporting.

### Câu hỏi 2: Có thể sử dụng dbt, Snowflake và thiết kế Data Mart được không?
**Câu trả lời là CỰC KỲ KHUYẾN KHÍCH.** Đây là kiến trúc chuẩn của **Modern Data Stack (MDS)** mà bất kỳ nhà tuyển dụng nào cũng tìm kiếm.
1.  **Thay Python bằng dbt ở bước Transform:**
    *   Thay vì viết các Consumer Python để join bảng phức tạp, bạn có thể load raw data trực tiếp từ Kafka/Staging vào Data Warehouse (EL - Extract & Load).
    *   Sau đó dùng **dbt** để thực hiện các câu lệnh SQL biến đổi dữ liệu (Transform) theo mô hình DAG (Direct Acyclic Graph), quản lý source, test và version control cực kỳ trực quan.
2.  **Sử dụng Snowflake làm Data Warehouse:**
    *   Dữ liệu từ production/staging có thể được đồng bộ lên Cloud Storage (như AWS S3) sau đó dùng **Snowpipe** để load tự động vào Snowflake.
    *   Snowflake sẽ đóng vai trò là Centralized DW lưu trữ Gold/Reporting Layer.
3.  **Thiết kế Data Mart:**
    *   Bảng `contract` (Wide Table) đóng vai trò là **ODS (Operational Data Store)** hoặc **Fact/Dimension Tables** (tại tầng Silver/DWH).
    *   Bảng phân tích hành vi `profiling_analysis` chính xác là một **Customer Profiling Data Mart** (tầng Gold). Bạn hoàn toàn có thể chia nhỏ thành các Data Mart khác như: *Claim & Risk Data Mart*, *Sales Performance Data Mart*, v.v.

> [!TIP]
> **Cách viết vào CV để ghi điểm tuyệt đối:**
> Bạn hãy viết rằng hệ thống hỗ trợ cả 2 luồng (Lambda Architecture):
> *   *Speed Layer (Real-time):* Python + Kafka + Redis để chống trùng lặp $O(1)$ và cập nhật giao diện Portal ngay lập tức.
> *   *Batch Layer (Analytical DWH):* Đồng bộ về Snowflake + dbt để phục vụ các báo cáo BI (PowerBI/Looker) và phân tích lịch sử chuyên sâu.

### Câu hỏi 3: Có nên lấy ý tưởng để build một project mới luôn không?
Việc này phụ thuộc vào quỹ thời gian và mục tiêu của bạn:

| Phương án | Ưu điểm | Nhược điểm | Khuyên dùng khi |
|---|---|---|---|
| **A. Giữ codebase cũ và khử nhãn (De-identify)** | * Tiết kiệm thời gian (code đã có sẵn bộ khung chạy ổn định).<br/>* Giữ được các logic phức tạp đã hoàn thiện. | * Phải rà soát kỹ để xóa sạch tên công ty và dữ liệu thực.<br/>* Công nghệ hơi mang tính custom (viết thuần Python nhiều). | Bạn muốn có dự án đưa vào CV **ngay lập tức** trong vòng 1-2 tuần tới. |
| **B. Build dự án mới dựa trên ý tưởng này** | * 100% sạch sẽ, không lo vi phạm bảo mật công ty.<br/>* Áp dụng được các công nghệ hot nhất (dbt, Snowflake, Airflow, Spark).<br/>* Code gọn gàng hơn vì bỏ được các logic nghiệp vụ đặc thù của công ty. | * Mất thời gian code lại từ đầu.<br/>* Cần đăng ký tài khoản cloud (như Snowflake trial) để demo. | Bạn có nhiều thời gian (3-4 tuần trở lên) và muốn hướng tới các vị trí **Mid/Senior Data Engineer** chuyên về Cloud Data Platform. |

---

## Part 2: Các Bước Chuyển Đổi Dự Án Hiện Tại Thành Dự Án Cá Nhân

Nếu bạn chọn **Phương án A** (Giữ codebase hiện tại và chỉnh sửa lại), dưới đây là các đầu việc bạn cần thực hiện:

### 1. Thay Đổi Tên Định Danh Thương Hiệu (De-branding)
Thay thế toàn bộ các tên liên quan đến công ty thành tên chung mang tính học thuật/cá nhân:
*   **Tên dự án:** `affina_portal_cdc` + `cdc_reporting` $\rightarrow$ **`ShieldFlow`** hoặc **`InsuStream-ETL`** (Hệ thống xử lý và phân tích dữ liệu bảo hiểm).
*   **Tên Database:** 
    *   `affina_sale` $\rightarrow$ `insure_production`
    *   `affina_staging` $\rightarrow$ `insure_staging`
    *   `affina_reporting` $\rightarrow$ `insure_analytics`
*   **Tên Bảng:** Giữ nguyên cấu trúc nhưng đổi tiền tố nếu cần (ví dụ: `stgContract` hay `stgClaim` giữ nguyên là tốt vì nó mang tính kỹ thuật).
*   **Thông tin giả lập (Mock Data):** Đổi toàn bộ các email từ `@affina.com.vn` thành `@example.com` hoặc `@insure.com`. Đổi tên nhà bảo hiểm (`BHV`, `PVI`) thành `InsureCorp`, `SafeGuard`, `Aegis`.

### 2. Xây Dựng Local Source DB & Script Generate Data
1.  **Tạo docker-compose.source-db.yml:**
    Tạo một container MySQL đại diện cho Production DB với cấu hình bật binlog:
    ```yaml
    services:
      production_db:
        image: mysql:8.0
        container_name: insure_production_db
        environment:
          MYSQL_ROOT_PASSWORD: root
          MYSQL_DATABASE: insure_production
        ports:
          - "3307:3306"
        command: --log-bin=mysql-bin --server-id=1 --binlog-format=ROW
    ```
2.  **Viết Script Sinh Dữ Liệu (`services/shared/generator.py`):**
    Sử dụng thư viện `Faker` trong Python để tự động insert dữ liệu ảo vào bảng `contract`, `contractObject`, `claim` sau mỗi 5-10 giây để người xem có thể nhìn thấy dữ liệu nhảy real-time qua Kafka.

### 3. Làm Sạch Lịch Sử Commit (Git History)
Vì trong lịch sử commit cũ có thể chứa các thông tin nhạy cảm của công ty, bạn **không nên** push trực tiếp repo này lên GitHub cá nhân mà chưa làm sạch:
*   **Cách tốt nhất:** Khởi tạo một Git repo hoàn toàn mới (xóa thư mục `.git` cũ đi và chạy `git init` lại từ đầu). Sau đó thực hiện commit đầu tiên là toàn bộ dự án đã được đổi tên và làm sạch. Việc này giúp lịch sử commit của bạn chỉ chứa các thông tin cá nhân.
