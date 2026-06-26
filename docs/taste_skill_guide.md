# Hướng dẫn Áp dụng & Sử dụng "taste-skill" cho Dự án InsuStream Portal

Tài liệu này hướng dẫn cách sử dụng và tối ưu hóa bộ quy tắc thiết kế cao cấp của **Leonxlnx/taste-skill** đã được cấu hình trong dự án CDC Reporting (`portal_frontend`).

---

## 1. Các thành phần đã được cài đặt vào Dự án

Chúng tôi đã cài đặt thành công 2 AI skills chính vào dự án để hỗ trợ phát triển:

1. **`design-taste-frontend`**: Lưu trữ tại `.\.agents\skills\design-taste-frontend\SKILL.md`. Đây là bộ quy tắc cốt lõi hướng dẫn thiết kế giao diện chống "AI slop" (giao diện chung chung, thiếu tinh tế).
2. **`stitch-design-taste`**: Lưu trữ tại `.\.agents\skills\stitch-design-taste\SKILL.md`. Bộ quy tắc giúp tự động sinh ra file `DESIGN.md` tối ưu hóa cho công cụ **Google Stitch** (StitchMCP) đang chạy trong hệ thống của bạn.
3. **`.cursorrules`**: Đã được tạo tại thư mục gốc của dự án. File này chứa các định hướng cấu hình nhanh được rút gọn từ `taste-skill` để các công cụ AI như **Cursor** hay **Claude Code** tự động đọc mỗi khi bạn bắt đầu một cuộc trò chuyện trong dự án.

---

## 2. Hướng dẫn sử dụng cho Lập trình viên

### Cách 1: Sử dụng tự động với Cursor hoặc Claude Code
Khi bạn mở dự án bằng Cursor hoặc chạy Claude Code tại thư mục gốc:
* Các công cụ AI này sẽ **tự động đọc** file `.cursorrules` ở thư mục gốc.
* Bạn chỉ cần mô tả tính năng cần xây dựng, AI sẽ tự động áp dụng các tiêu chuẩn thiết kế (như sử dụng font chữ hình học, tránh màu neon, thiết kế layout bất đối xứng, viết CSS có chuyển động mượt mà).

### Cách 2: Gọi trực tiếp Skill khi chat với AI
Nếu bạn muốn AI tập trung cao độ vào việc cải tiến thiết kế của một màn hình cụ thể, hãy nhắc AI sử dụng trực tiếp file skill đã cài đặt:

> **Ví dụ Prompt:**
> *"Hãy đọc file quy tắc tại `.agents/skills/design-taste-frontend/SKILL.md` và viết lại CSS cho `UploadForm.css` để giao diện trông cao cấp hơn, tăng độ tương tác và thêm hiệu ứng loading skeleton thay thế cho spinner tròn hiện tại."*

---

## 3. Quy chuẩn viết CSS cao cấp trong Dự án (Vanilla CSS)

Vì dự án `portal_frontend` của bạn sử dụng **Vanilla CSS** (không dùng Tailwind), việc áp dụng thiết kế cao cấp cần tuân thủ các ví dụ thực tiễn dưới đây:

### A. Định nghĩa Hệ màu HSL & Spacing ở `index.css`
Thay vì viết cứng mã màu Hex rải rác, hãy khai báo các biến CSS tại `:root` để dễ quản lý và chuyển đổi Light/Dark mode:

```css
:root {
  /* Neutral Canvas - Màu nền tối giản, sang trọng */
  --bg-canvas: #f8fafc;
  --bg-surface: #ffffff;
  
  /* Typography Ink - Màu chữ độ tương phản cao */
  --text-primary: #0f172a;
  --text-muted: #64748b;
  
  /* Brand Accent - Điểm nhấn xanh hoàng gia sang trọng (không dùng neon) */
  --color-accent: #2563eb;
  --color-accent-hover: #1d4ed8;
  
  /* Status Colors */
  --color-success: #059669;
  --color-error: #e11d48;
  --color-warning: #d97706;
  
  /* Borders & Shadows */
  --border-subtle: rgba(226, 232, 240, 0.8);
  --shadow-premium: 0 4px 6px -1px rgba(0, 0, 0, 0.05), 0 2px 4px -2px rgba(0, 0, 0, 0.05);
}
```

### B. Micro-interactions cho Nút (Button) & Dropzone
Thêm các hiệu ứng dịch chuyển nhẹ (tactile feedback) và chuyển động mượt mà thay vì thay đổi trạng thái đột ngột:

```css
/* Nút bấm có hiệu ứng lún xuống khi nhấn (Tactile Feedback) */
.upload-button {
  background-color: var(--color-accent);
  color: #ffffff;
  border: none;
  border-radius: 8px;
  padding: 10px 20px;
  font-weight: 500;
  transition: all 0.2s cubic-bezier(0.4, 0, 0.2, 1);
  box-shadow: var(--shadow-premium);
  cursor: pointer;
}

.upload-button:hover {
  background-color: var(--color-accent-hover);
  transform: translateY(-1px);
}

.upload-button:active {
  transform: translateY(1px);
}

/* Dropzone có viền nét đứt chuyển động khi kéo file vào */
.dropzone {
  border: 2px dashed var(--border-subtle);
  border-radius: 12px;
  transition: all 0.2s ease-in-out;
}

.dropzone.drag-active {
  border-color: var(--color-accent);
  background-color: rgba(37, 99, 235, 0.02);
  transform: scale(1.01);
}
```

### C. Thay thế Spinner mặc định bằng Shimmer Skeleton Loader
Để người dùng có trải nghiệm trực quan tốt khi tải dữ liệu, thay vì dùng biểu tượng xoay vòng tròn đơn điệu, hãy sử dụng skeleton:

```css
/* Hiệu ứng quét sáng (Shimmer effect) */
@keyframes shimmer {
  0% {
    background-position: -200% 0;
  }
  100% {
    background-position: 200% 0;
  }
}

.skeleton-loader {
  width: 100%;
  height: 20px;
  border-radius: 4px;
  background: linear-gradient(90deg, #f1f5f9 25%, #e2e8f0 50%, #f1f5f9 75%);
  background-size: 200% 100%;
  animation: shimmer 1.5s infinite;
}
```

---

## 4. Tích hợp với Google Stitch (StitchMCP)

Nếu bạn muốn tạo mới giao diện bằng công cụ sinh màn hình của Google Stitch:

1. **Sinh file DESIGN.md**: Nhắc AI của bạn:
   > *"Hãy dùng luật `stitch-design-taste` để viết một file `DESIGN.md` mô tả thiết kế của dự án InsuStream Portal của tôi."*
2. **Đồng bộ hóa với Stitch**: Sử dụng công cụ MCP `upload_design_md` của StitchMCP để đẩy file `DESIGN.md` vừa tạo lên hệ thống.
3. **Sinh màn hình**: Sử dụng `create_design_system_from_design_md` để cập nhật hệ thống và bắt đầu tạo các màn hình mới với giao diện chuẩn hóa và cao cấp.
