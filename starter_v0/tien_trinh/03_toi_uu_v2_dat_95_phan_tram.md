# 🚀 Tiến Trình 03: Tối Ưu Vòng v2 — Đạt 95% Case Accuracy & 100% Routing!

- **Thời gian hoàn thành:** 10:50 AM
- **Người thực hiện:** Quang (Nhánh `lab/prompt`)
- **Tập tin thay đổi:** [artifacts/tools.yaml](file:///c:/Users/buida/vinuni_day03_lab/K5-L3A-DAY03-GG-Prompt-Function-Calling-Tool-Design-MCP-/starter_v0/artifacts/tools.yaml) và [artifacts/system_prompt.md](file:///c:/Users/buida/vinuni_day03_lab/K5-L3A-DAY03-GG-Prompt-Function-Calling-Tool-Design-MCP-/starter_v0/artifacts/system_prompt.md)
- **File run kết quả:** [runs/v2_B_base_gemini_20261110T104952520561.json](file:///c:/Users/buida/vinuni_day03_lab/K5-L3A-DAY03-GG-Prompt-Function-Calling-Tool-Design-MCP-/starter_v0/runs/v2_B_base_gemini_20261110T104952520561.json)

---

## 1. Giả Thuyết Tối Ưu Vòng `v2` (Hypothesis)

> **Giả thuyết:** Kết quả từ `v1` cho thấy model đã hiểu luồng nhưng còn sai sót do khai báo tool trong `tools.yaml` còn chung chung:
> 1. `clarify` chưa bắt buộc tham số `response_type` (`required: [question, response_type]`).
> 2. Model tự ý mở rộng từ viết tắt (đổi "AI" thành "Artificial Intelligence").
> 3. Lượt multi-turn kế tiếp không nhận biết câu trả lời bổ sung từ user.
> 
> → Giải pháp: Viết lại toàn bộ mô tả của từng tool trong [artifacts/tools.yaml](file:///c:/Users/buida/vinuni_day03_lab/K5-L3A-DAY03-GG-Prompt-Function-Calling-Tool-Design-MCP-/starter_v0/artifacts/tools.yaml), nêu rõ trường hợp khi nào dùng / khi nào KHÔNG dùng, quy định bắt buộc `response_type`, và bổ sung quy tắc bảo toàn chữ viết tắt trong `system_prompt.md`.

---

## 2. Bảng So Sánh Bước Nhảy Vọt Metrics (v0 → v1 → v2)

| Chỉ số | Baseline `v0` | Vòng `v1` | Vòng `v2` | Tiến bộ v0 → v2 |
|---|:---:|:---:|:---:|:---:|
| **Case Accuracy** | 65.0% (13/20) | 76.47% (13/17) | **95.0% (19/20)** | 🟢 **+30.0%** |
| **Tool Routing Accuracy** | 80.0% (16/20) | 94.12% (16/17) | **100.0% (20/20)** | 🟢 **+20.0% (HOÀN HẢO)** |
| **Argument Accuracy** | 65.0% (13/20) | 76.47% (13/17) | **95.0% (19/20)** | 🟢 **+30.0%** |
| **Multiturn Accuracy** | 66.67% (4/6) | 66.67% (2/3) | **100.0% (6/6)** | 🟢 **+33.33% (HOÀN HẢO)** |
| **Provider Errors** | 0 | 3 | **0** | Tuyệt đối ổn định |

- **Artifact Version:** `v2+pd934795af904+t500538c44d95`
- **Prompt Hash:** `d934795af9042b36a7a58a741ef035d2d46e3a9c7b99c73efaa71ca53c65c4ec`
- **Tools Hash:** `500538c44d953ce0a365f5a8c9e6ca337ae61cf6f888f40776b251a37c568f61`

---

## 3. Phân Tích Chi Tiết Các Case (19/20 Đã PASS)

- **19/20 Case PASS Xanh Hoàn Toàn:**
  - Toàn bộ các test multi-turn M01 → M06 đạt 100%.
  - Toàn bộ các test routing, limit, timeframe, search_type, parallel tool calls đạt 100%.
  - `R03_web_news_routing`: Đã PASS (giữ đúng `query='AI'`, `topic='news'`, `timeframe='day'`).
  - `R11_missing_url`: Đã PASS (gọi đúng `clarify` kèm `response_type='text'`).
  - `M01_clarify_then_fill`: Đã PASS (nhận diện được câu trả lời ở lượt 2 và gọi `timeline`).

- **Chỉ còn đúng 1 case duy nhất chưa pass:**
  - **`R12_confirm_before_send`**:
    - *Query:* "Gửi bản tin này lên kênh Telegram của team".
    - *Expect:* `clarify(response_type="yes_no")` (hỏi: "Bạn có chắc chắn muốn gửi không?").
    - *Actual:* Model hỏi: "Bạn muốn gửi nội dung nào?" với `response_type="text"`.
    - *Nguyên nhân:* Prompt chưa nhấn mạnh là khi có yêu cầu "Gửi/Đăng" thì mặc định câu hỏi xác nhận phải luôn là kiểu `yes_no`.

---

## 4. Kế Hoạch Cho Vòng `v3` & Tích Hợp

1. **Sửa nhẹ quy tắc xác nhận Telegram** trong `system_prompt.md` để đạt trọn vẹn **100% (20/20 cases)** cho vòng `v3`.
2. **Ghép Tool mới của Đạt (`domain_summary`)**:
   - Khi Đạt bàn giao xong code `tools/domain_summary/tool.py` và `TOOL.md`, Quang sẽ khai báo thêm tool này vào cuối file `artifacts/tools.yaml`.
   - Chạy lại eval để tạo bản nộp chính thức `v3` hoàn chỉnh nhất!

