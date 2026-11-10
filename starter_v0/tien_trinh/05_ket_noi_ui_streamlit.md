# 🖥️ Tiến Trình 05: Kết Nối Agent Vào Giao Diện Streamlit (`app.py`)

- **Thời gian hoàn thành:** 11:55 AM (Vượt xa mốc deadline 16:30)
- **Người thực hiện:** Hùng & Quang
- **File giao diện:** [starter_v0/app.py](file:///c:/Users/buida/vinuni_day03_lab/K5-L3A-DAY03-GG-Prompt-Function-Calling-Tool-Design-MCP-/starter_v0/app.py)

---

## 1. Tích Hợp Kỹ Thuật

1. **Cài đặt Streamlit:** Đã hoàn tất cài đặt `streamlit` và toàn bộ các dependencies đồ họa liên quan (`altair`, `pandas`, `pydeck`, v.v.).
2. **Cấu hình tự động nhận diện Provider:**
   - Trong `app.py`, cấu hình mặc định tự động chọn `gemini` khi phát hiện `GEMINI_API_KEY` trong file `.env`.
   - Kết nối trực tiếp vào vòng lặp agent `run_model_tool_loop()` từ `chat.py`.
3. **Cập nhật Tool Metadata:**
   - Đã thêm tool mới `domain_summary` vào danh mục `TOOL_META` trong giao diện để người dùng có thể thấy icon và mô tả của tool này trên giao diện trực quan.
4. **Hoàn thiện Phần A Báo Cáo:**
   - Đã điền đầy đủ Phần A (Giới thiệu agent, danh mục tool có kèm tool mới `domain_summary`, 5 câu hỏi mẫu để test live) trong [artifacts/REPORT.md](file:///c:/Users/buida/vinuni_day03_lab/K5-L3A-DAY03-GG-Prompt-Function-Calling-Tool-Design-MCP-/starter_v0/artifacts/REPORT.md).

---

## 2. Hướng Dẫn Chạy Thử Giao Diện Local

Chạy lệnh sau tại thư mục `starter_v0/`:

```bash
cd starter_v0
streamlit run app.py
```

Trình duyệt sẽ tự động mở tại địa chỉ: `http://localhost:8501`.

---

## 3. Expose Link Demo Bằng Cloudflare Tunnel (Cho Buổi Showdown 16:30)

Để các nhóm khác trong lớp có thể mở link và test thử agent ngay trên máy của họ:
1. Mở một terminal mới và chạy:
   ```bash
   cloudflared tunnel --url http://localhost:8501
   ```
2. Copy đường link sinh ra (dạng `https://xxxx.trycloudflare.com`) và dán vào mục **Link dùng thử** trong `artifacts/REPORT.md`!

