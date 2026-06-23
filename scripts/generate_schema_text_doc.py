import mysql.connector
from collections import defaultdict

config = {
    'host': 'localhost',
    'port': 3306,
    'user': 'synthetic_db_user',
    'password': 'REDACTED_PASSWORD'
}

try:
    conn = mysql.connector.connect(**config)
    cursor = conn.cursor(dictionary=True)

    print("Fetching tables...")
    cursor.execute("""
    SELECT TABLE_SCHEMA, TABLE_NAME, TABLE_COMMENT 
    FROM information_schema.TABLES 
    WHERE TABLE_SCHEMA NOT IN ('information_schema', 'mysql', 'performance_schema', 'sys')
    ORDER BY TABLE_SCHEMA, TABLE_NAME
    """)
    tables = cursor.fetchall()
    
    # Group tables by schema
    db_dict = defaultdict(list)
    for row in tables:
        db_dict[row['TABLE_SCHEMA']].append(row)

    print("Generating text-based markdown...")
    markdown_content = "# Hướng Dẫn Chi Tiết Dữ Liệu Các Database Sandbox\n\n"
    markdown_content += "Tài liệu này giải thích bằng văn bản về mục đích của từng database và chức năng lưu trữ của từng bảng (table) bên trong hệ thống sandbox (localhost), giúp người đọc dễ dàng hình dung cấu trúc dữ liệu tổng thể.\n\n"
    
    db_descriptions = {
        "affina_authentication": "Quản lý xác thực, phân quyền người dùng (cả người dùng cuối và admin), lưu trữ token và cấu hình đăng nhập SSO (Google, Facebook, Apple).",
        "affina_normalize": "Lưu trữ dữ liệu đã được chuẩn hóa (normalize) từ các hệ thống hoặc định dạng khác nhau về chuẩn chung của hệ thống Affina, hỗ trợ quá trình ETL và đồng bộ.",
        "affina_notification": "Quản lý toàn bộ hệ thống thông báo đa kênh, bao gồm template tin nhắn, cấu hình gửi và lịch sử gửi qua Email, SMS, Push Notification.",
        "affina_other": "Lưu trữ các dữ liệu phụ trợ, nội dung hiển thị (banner, video, event), thông tin ngân hàng, và các cấu hình động không thuộc các luồng nghiệp vụ chính.",
        "affina_partner": "Quản lý thông tin đối tác phân phối, thông tin API tích hợp, đại lý, và các giao dịch, chiến dịch liên quan tới đối tác B2B.",
        "insuranceReporting": "Chứa các bảng dữ liệu tổng hợp (Data Mart/Data Warehouse thu nhỏ) phục vụ riêng cho việc xuất báo cáo, thống kê, và xây dựng biểu đồ BI.",
        "insuranceSale": "Quản lý luồng kinh doanh (Sale), chứa thông tin cốt lõi về hợp đồng, chứng nhận bảo hiểm, giao dịch thanh toán, hóa đơn và tiến trình bán hàng.",
        "insuranceWarehouse": "Vùng dữ liệu đệm (Staging Area), lưu trữ dữ liệu thô (raw) tạm thời được CDC hoặc ETL đẩy vào trước khi xử lý, làm sạch và chuyển vào Data Warehouse.",
        "affina_user": "Quản lý hồ sơ người dùng cuối (End-User), thông tin cá nhân, định danh, địa chỉ, lịch sử hành động và các cấu hình ưu tiên của người dùng.",
        "affina_zalo_context": "Quản lý trạng thái, ngữ cảnh (context), webhook, và các cấu hình liên quan đến việc tích hợp sâu với nền tảng Zalo (Zalo Mini App, ZOA).",
        "core_auth": "Dịch vụ Core lõi về quản lý thông tin xác thực, phân quyền cấp thấp, token bảo mật, và phiên đăng nhập của toàn hệ thống.",
        "core_claim": "Dịch vụ Core lõi quản lý quy trình giải quyết quyền lợi bảo hiểm (bồi thường/claim), hồ sơ bệnh án, trạng thái chi trả và lịch sử bồi thường.",
        "core_loyalty": "Dịch vụ Core lõi quản lý chương trình khách hàng thân thiết, điểm thưởng (point), hạng thành viên, mã giảm giá (voucher) và quà tặng.",
        "core_meta": "Dịch vụ Core lõi lưu trữ siêu dữ liệu (metadata), danh mục hệ thống (Master Data) như tỉnh/thành phố, nghề nghiệp, trạng thái động.",
        "core_policy": "Dịch vụ Core lõi quản lý các quy tắc nghiệp vụ bảo hiểm, chính sách điều khoản, và logic tính phí bảo hiểm.",
        "core_post": "Dịch vụ Core lõi quản lý nội dung dạng bài viết (CMS), tin tức, bài blog, câu hỏi thường gặp (FAQ) được hiển thị trên hệ thống.",
        "core_product": "Dịch vụ Core lõi quản lý danh mục sản phẩm bảo hiểm, cấu trúc gói bảo hiểm, quyền lợi chi tiết và nhà cung cấp.",
        "core_push": "Dịch vụ Core lõi xử lý hệ thống queue và worker để đẩy Push Notification tốc độ cao tới các thiết bị di động/web.",
        "core_stakeholder": "Dịch vụ Core lõi quản lý hồ sơ các bên liên quan bao gồm nhà bảo hiểm, bệnh viện/phòng khám (TPA), đối tác doanh nghiệp.",
        "prod_affina_other": "Bản lưu trữ hoặc dữ liệu ánh xạ từ hệ thống Production cho module affina_other, dùng để đối soát hoặc test luồng production.",
        "prod_insuranceSale": "Bản lưu trữ hoặc dữ liệu ánh xạ từ hệ thống Production cho module insuranceSale, chứa dữ liệu kinh doanh thực tế.",
        "prod_affina_user": "Bản lưu trữ hoặc dữ liệu ánh xạ từ hệ thống Production cho module affina_user, chứa dữ liệu người dùng thực tế.",
        "profiling_analysis": "Chứa các dữ liệu log, footprint, trackings phục vụ cho việc phân tích hành vi người dùng, đánh giá hiệu năng (profiling) và phân tích dữ liệu (Data Analysis).",
        "sys": "Database hệ thống mặc định của MySQL, chứa các view và thông tin nội bộ của server (không chứa dữ liệu nghiệp vụ)."
    }

    for schema in sorted(db_dict.keys()):
        tbls = db_dict[schema]
        markdown_content += f"## 🗄️ Database: `{schema}`\n"
        
        desc = db_descriptions.get(schema, f"Database `{schema}` chứa các dữ liệu liên quan đến hệ thống phân hệ {schema}.")
        markdown_content += f"**Mục đích:** {desc}\n\n"
        markdown_content += "**Giải thích các bảng (Tables) trong Database:**\n\n"
        
        for tbl in tbls:
            table_name = tbl['TABLE_NAME']
            table_comment = tbl['TABLE_COMMENT']
            if not table_comment:
                # Tạo mô tả logic dựa trên tên table nếu không có comment
                if table_name.startswith("nor"):
                    table_comment = f"Lưu trữ dữ liệu {table_name.replace('nor', '')} đã được chuẩn hóa (normalize) từ các nguồn khác."
                elif table_name.startswith("core"):
                    table_comment = f"Lưu trữ dữ liệu lõi của đối tượng {table_name} trong hệ thống."
                elif "history" in table_name.lower() or "log" in table_name.lower():
                    table_comment = f"Lưu trữ lịch sử/nhật ký các thao tác hoặc thay đổi liên quan đến {table_name}."
                elif "config" in table_name.lower() or "setting" in table_name.lower():
                    table_comment = f"Lưu trữ các cài đặt, cấu hình của hệ thống cho {table_name}."
                else:
                    table_comment = f"Lưu trữ dữ liệu chi tiết của đối tượng `{table_name}`."
            
            # Xử lý xuống dòng trong comment
            table_comment = table_comment.replace('\n', ' ').replace('\r', '').strip()
            markdown_content += f"- **`{table_name}`**: {table_comment}\n"
        
        markdown_content += "\n---\n\n"

    with open('docs/sandbox_databases_text_description.md', 'w', encoding='utf-8') as f:
        f.write(markdown_content)
        
    print("Markdown file generated successfully at docs/sandbox_databases_text_description.md")

except Exception as e:
    print(f"Error: {e}")
finally:
    if 'cursor' in locals() and cursor is not None:
        cursor.close()
    if 'conn' in locals() and conn.is_connected():
        conn.close()
