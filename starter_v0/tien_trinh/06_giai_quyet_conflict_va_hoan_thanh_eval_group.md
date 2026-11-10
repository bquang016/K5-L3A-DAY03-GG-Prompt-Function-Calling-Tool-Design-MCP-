# Tiến trình 06: Giải quyết Conflict, Hoàn thành Eval Group & Live Chat Agent

**Thời gian:** 12:20 - 10/11/2026  
**Người phụ trách:** Quang (`lab/prompt` - điều phối)  
**Tình trạng:** Hoàn thành xuất sắc (All Green 100%)

---

## 1. Công việc đã thực hiện

### A. Xử lý triệt để Merge Conflict
- **File `data/eval_group.json`:**
  - Đồng bộ và tích hợp đầy đủ 10 test cases (5 single-turn + 5 multi-turn) bao quát các kịch bản thực tế: kiểm tra tool mới `domain_summary`, xử lý đại từ xưng hô thiếu ngữ cảnh (`clarify`), guardrail xác nhận trước khi gửi Telegram (`send`), loại bỏ nhiễm ngữ cảnh đa lượt và từ chối yêu cầu ngoài phạm vi (`out_of_scope`).
- **File `tests/test_tools_todo.py`:**
  - Sửa lỗi cú pháp do conflict lúc merge PR.
  - Tích hợp toàn diện các bài test cho toàn bộ công cụ (`clarify`, `format`, `send`, `lookup`, `fetch`, `timeline`, `social_search`, `policy`) và kiểm thử chi tiết cho tool mới `domain_summary` (happy path, gộp domain www, bắt URL rác, kiểm tra kiểu dữ liệu).
  - Kết quả chạy `pytest tests/ -v`: **92/92 passed (100% xanh, 0 failed, 0 skipped)**.

### B. Chạy đánh giá bộ test nhóm (Group Eval)
- Lệnh chạy:
  ```bash
  python run_eval.py --provider gemini --suite group --eval-cases data/eval_group.json --phase B --version v3
  ```
- **Kết quả:**
  - **10/10 Cases PASS (100% Case Accuracy)**
  - **100% Tool Routing Accuracy**
  - **100% Argument Accuracy**
  - **100% Multi-turn Accuracy**
  - File kết quả lưu tại: `runs/v3_B_group_gemini_20261110T121955980021.json`

### C. Chạy thực tế Live Chat đa lượt (Agent Live Verification)
- Khởi chạy phiên hội thoại thực tế đa lượt với Agent phiên bản v3 qua Gemini:
  - **Lượt 1:** Yêu cầu tra cứu tin tức AI hôm nay -> Agent gọi `lookup` và `format`, xuất bản tin tổng hợp dạng Markdown Digest theo chủ đề có trích dẫn nguồn.
  - **Lượt 2:** Yêu cầu thống kê domain từ 3 link cung cấp -> Agent gọi chính xác tool mới `domain_summary`, phân tích chính xác tần suất xuất hiện từng domain.
  - **Lượt 3:** Người dùng gửi lời cảm ơn -> Agent đối thoại lịch sự, không gọi tool dư thừa.
- File transcript tạo thành: `transcripts/v3_gemini_20261110T122042024241.transcript.json`.

### D. Hoàn thiện báo cáo toàn diện `artifacts/REPORT.md`
- Đã điền đầy đủ cả **Phần A** (A1, A2, A3) và **Phần B** (B1: Version Evidence, B2: Failure Analysis chi tiết từ v0, B3: 10 Group Eval Cases, B4: Live Chat Evidence, B5: Bonus Guardrail, Injection Defense, UI & Unit Tests).
