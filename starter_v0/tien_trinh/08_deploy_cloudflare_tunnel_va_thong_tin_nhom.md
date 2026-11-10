# Tiến trình 08: Khởi chạy Cloudflare Tunnel Public & Hoàn thiện Thông tin Sinh viên

**Thời gian:** 16:55 - 10/11/2026  
**Người phụ trách:** Bùi Đăng Quang (`lab/prompt` - điều phối nhóm)  
**Tình trạng:** Hoàn tất xuất sắc — Link public đã LIVE 100%

---

## 1. Công việc thực hiện

### A. Tải và Thiết lập Cloudflare Tunnel
- Tải binary `cloudflared.exe` phiên bản chính thức (2026.10.7).
- Viết script quản lý `start_tunnel.py` tự động khởi chạy đồng bộ:
  - Streamlit UI trên port 8501.
  - Cloudflare Tunnel trỏ về `http://localhost:8501`.
- Quá trình chạy ngầm liên tục (daemon) để giữ link hoạt động xuyên suốt phiên làm việc.

### B. Địa chỉ Public URL
- **Public Cloudflare Tunnel Live Link:**
  `https://property-facts-expires-included.trycloudflare.com`
- Kiểm thử trạng thái qua curl: **HTTP/1.1 200 OK** (Đã xác minh truy cập thành công từ internet).

### C. Cập nhật Báo cáo `artifacts/REPORT.md`
- Đã điền chính xác link public vào mục **Phần A1: Link dùng thử (deploy)**.
- Đã cập nhật danh sách thành viên và MSSV đầy đủ:
  - **Bùi Đăng Quang** - MSSV: `2A202603640`
  - **Nguyễn Đức Trọng** - MSSV: `2A202603644`
  - **Trịnh Quốc Đạt** - MSSV: `2A202603581`
  - **Nguyễn Xuân Hùng** - MSSV: `2A202603599`
- Đã cập nhật link trực tiếp và thông tin nhóm vào **[artifacts/poster.html](file:///c:/Users/buida/vinuni_day03_lab/K5-L3A-DAY03-GG-Prompt-Function-Calling-Tool-Design-MCP-/starter_v0/artifacts/poster.html)**.
