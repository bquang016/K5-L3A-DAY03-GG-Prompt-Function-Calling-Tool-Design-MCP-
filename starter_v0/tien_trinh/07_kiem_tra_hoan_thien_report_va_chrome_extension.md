# Tiến trình 07: Kiểm tra Hoàn thiện Báo cáo (Phần A & B) & Bổ sung Bonus Chrome Extension

**Thời gian:** 14:12 - 10/11/2026  
**Người phụ trách:** Quang (`lab/prompt` - điều phối) & Hùng (`lab/ui`)  
**Tình trạng:** Hoàn tất 100% — Sẵn sàng cho buổi Showdown 16:30 và nộp bài cuối giờ

---

## 1. Kiểm tra đối chiếu yêu cầu nhiệm vụ

### A. PHẦN A — Giới thiệu agent (Hoàn thành trước 16:30)
- **A1. Chức năng Agent:**
  - Mô tả đầy đủ năng lực nghiên cứu chuyên sâu: tra cứu tin tức Tavily, tweet X/Twitter, trích xuất Firecrawl, arXiv, phân tích domain (`domain_summary`), guardrail Telegram.
  - Tích hợp 2 hình thức UI: **Web Studio Streamlit** (`app.py`) và **Chrome Extension Sider Mode** (`chrome_extension/`).
  - Hướng dẫn deploy public link bằng Cloudflare Tunnel (`cloudflared tunnel --url http://localhost:8501`).
- **A2. Bảng Tool:**
  - Liệt kê đầy đủ 11 công cụ.
  - Nêu rõ tool mới của nhóm phát triển: `domain_summary`.
- **A3. Bộ câu hỏi mẫu:**
  - 5 câu hỏi mẫu rõ ràng, tương ứng với 5 tình huống thử nghiệm (tra cứu, map handle Twitter, đếm tên miền bằng tool mới, an toàn thiếu URL và guardrail xác nhận Telegram).
- **Tài liệu phụ trợ Showdown:**
  - Đã xuất bản poster giới thiệu trực quan tại `artifacts/poster.html`.

### B. PHẦN B — Chi tiết / Bằng chứng (Hoàn thành trước khi nộp bài)
- **B1. Version Evidence:**
  - Ghi nhận đầy đủ hành trình tối ưu từ v0 (65.0%) -> v1 (76.5%) -> v2 (95.0%) -> **v3 (100.0% Base 20/20 & Group 10/10)**.
  - Liên kết chính xác các run log JSON trong thư mục `runs/`.
- **B2. Failure Analysis:**
  - Phân tích chi tiết 7 lỗi quan sát ở v0: R03, R10, R11, R12, R13, M02, M06 và giải pháp khắc phục.
- **B3. Team Eval Cases:**
  - Đầy đủ 10 ca kiểm thử của nhóm trong `data/eval_group.json` (5 single-turn, 5 multi-turn), ghi nhận kết quả 10/10 PASS.
- **B4. Live Chat Evidence:**
  - Trích dẫn trực tiếp từ file transcript thật: `transcripts/v3_gemini_20261110T122042024241.transcript.json`.
- **B5. Bonus Evidence:**
  - Telegram Guardrail (bắt buộc xác nhận yes/no).
  - Policy & arXiv (lọc prompt injection sang `untrusted_text`).
  - Web UI Streamlit Studio (`app.py`).
  - **Chrome Extension Sider Mode (`chrome_extension/`):** Tiện ích mở rộng Side Panel Manifest V3 cho trình duyệt Chrome.
  - Tool Unit Tests: 92/92 tests xanh 100% trong `tests/test_tools_todo.py`.

