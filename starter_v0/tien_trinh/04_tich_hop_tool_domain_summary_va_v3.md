# 🛠️ Tiến Trình 04: Review Code Của Đạt, Tích Hợp Tool Mới & Chạy Bản v3

- **Thời gian hoàn thành:** 11:26 AM (Vượt xa tiến độ mốc 15:30)
- **Người thực hiện:** Quang & Đạt
- **Tool mới:** `domain_summary` (Thư mục: `tools/domain_summary/`)
- **File run kết quả v3:** [runs/v3_B_base_gemini_20261110T112600283045.json](file:///c:/Users/buida/vinuni_day03_lab/K5-L3A-DAY03-GG-Prompt-Function-Calling-Tool-Design-MCP-/starter_v0/runs/v3_B_base_gemini_20261110T112600283045.json)

---

## 1. Kết Quả Review Code Của Đạt (`lab/tool`)

Đạt đã hoàn thành xuất sắc các yêu cầu cơ bản trong phân công nhiệm vụ:
- Đã tạo `tools/domain_summary/tool.py` và `tools/domain_summary/TOOL.md`.
- Đã đăng ký hàm vào `tools/__init__.py`.
- Đã khai báo schema của `domain_summary` vào cuối file `artifacts/tools.yaml`.
- Đã viết 4 unit test trong `tests/test_tools_todo.py`.

### 🔍 Các lỗi kỹ thuật đã được phát hiện và fix ngay lập tức:
1. **Lỗi lệch Output Key giữa test và implementation:**
   - Trong `tool.py`, Đạt trả về key `"domains"`, nhưng trong `test_tools_todo.py` và `TOOL.md` lại assert `result["domain_counts"]` -> Dẫn tới `KeyError: 'domain_counts'`.
   - *Đã xử lý:* Cập nhật hàm trả về cả hai key `"domain_counts"` và `"domains"`.
2. **Lỗi xử lý URL không hợp lệ theo Contract:**
   - Khi gặp URL sai hoặc kiểu dữ liệu không phải string (như số 123), test kỳ vọng trả về dict lỗi có key `"error"` và `"tool": "domain_summary"`. Ban đầu hàm chỉ gom vào list `invalid` mà không trả `"error"` nếu còn URL khác hợp lệ.
   - *Đã xử lý:* Nếu danh sách URL có bất kỳ URL lỗi nào, hàm trả về ngay dict lỗi theo đúng chuẩn starter: `{"tool": "domain_summary", "error": ...}`.
3. **Lỗi vô tình xóa trắng `.env.example`:**
   - Đạt commit làm trống file `starter_v0/.env.example`.
   - *Đã xử lý:* Khôi phục lại file gốc nguyên vẹn.

---

## 2. Kết Quả Kiểm Thử (100% XANH)

- Chạy `pytest -v`: **71 passed, 14 skipped, 0 failed!**
  - 57 contract tests: **PASSED** (tools.yaml <-> signatures <-> TOOL.md đồng bộ 100%).
  - 4 unit tests của `domain_summary`: **PASSED XANH HOÀN TOÀN**.

---

## 3. Kết Quả Chạy Đánh Giá Bản Tích Hợp `v3`

Chạy lại toàn bộ `eval_base.json` trên bản đã ghép tool mới:
- **Case Accuracy:** **19 / 20 (95.0%)**
- **Tool Routing Accuracy:** **20 / 20 (100.0% Tuyệt đối)**
- **Multiturn Accuracy:** **6 / 6 (100.0% Tuyệt đối)**
- **Provider Errors:** **0**
- **Artifact Version:** `v3+pf4156eb7a35f+tb74750c49704`

Bản `v3` chính thức đã được ghi vào [artifacts/version_log.csv](file:///c:/Users/buida/vinuni_day03_lab/K5-L3A-DAY03-GG-Prompt-Function-Calling-Tool-Design-MCP-/starter_v0/artifacts/version_log.csv).

