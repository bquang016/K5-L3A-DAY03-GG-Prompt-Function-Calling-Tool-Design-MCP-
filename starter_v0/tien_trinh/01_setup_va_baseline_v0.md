# 🚀 Tiến Trình 01: Setup Môi Trường & Chạy Đánh Giá Baseline v0

- **Thời gian hoàn thành:** 10:40 AM (vượt trước deadline checkpoint 15:00)
- **Người thực hiện:** Quang (Nhánh `lab/prompt`)
- **Model chốt sử dụng:** `gemini-3.5-flash-lite` (Provider: Google GenAI)
- **File run kết quả:** [runs/v0_B_base_gemini_20261110T104036405787.json](file:///c:/Users/buida/vinuni_day03_lab/K5-L3A-DAY03-GG-Prompt-Function-Calling-Tool-Design-MCP-/starter_v0/runs/v0_B_base_gemini_20261110T104036405787.json)

---

## 1. Các Công Việc Kỹ Thuật Đã Hoàn Thành

1. **Khởi tạo và kiểm tra file `.env`**:
   - Khai báo đầy đủ các key: `GEMINI_API_KEY`, `TAVILY_API_KEY`, `FIRECRAWL_API_KEY`, `RAPIDAPI_KEY`.
   - Cấu hình chuẩn `RAPIDAPI_TWITTER_HOST=twitter-api45.p.rapidapi.com` và `ARXIV_USER_AGENT`.
   - Xác nhận `.env` đã được git ignore an toàn ở cả root và `starter_v0/`.
2. **Cài đặt gói phụ thuộc (`requirements.txt`)**:
   - Đã cài đặt đầy đủ: `google-genai>=0.8.0`, `openai`, `anthropic`, `requests`, `PyYAML`, `pypdf`, `pytest`.
3. **Chạy kiểm thử hợp đồng (`pytest`)**:
   - Chạy lệnh `pytest` trong `starter_v0/`: **62 passed, 17 skipped** (100% contract test và example test xanh; 17 stubs TODO dành cho Đạt đang skipped đúng tiêu chuẩn).
4. **Smoke test Preflight Provider**:
   - Đã chạy lệnh: `python scripts/preflight_provider.py --provider gemini`
   - Kết quả: `OK provider=gemini model=gemini-3.5-flash-lite` (gọi đúng tool `timeline` với argument `screenname="sama"`).
5. **Ghi nhận lịch sử versioning**:
   - Đã ghi dòng `v0` vào [artifacts/version_log.csv](file:///c:/Users/buida/vinuni_day03_lab/K5-L3A-DAY03-GG-Prompt-Function-Calling-Tool-Design-MCP-/starter_v0/artifacts/version_log.csv).

---

## 2. Kết Quả Đo Lường Baseline `v0`

Chạy trên tập dữ liệu cố định [data/eval_base.json](file:///c:/Users/buida/vinuni_day03_lab/K5-L3A-DAY03-GG-Prompt-Function-Calling-Tool-Design-MCP-/starter_v0/data/eval_base.json) (20 cases: 14 single-turn, 6 multi-turn).

| Chỉ số (Metric) | Kết quả Baseline v0 | Đánh giá |
|---|:---:|---|
| **Tổng số case** | 20 | Đã đo toàn bộ |
| **Provider Error** | **0** (0%) | API gọi mượt, không lỗi mạng/quota |
| **Case Accuracy** | **13 / 20 (65.0%)** | Điểm khởi đầu tốt để tối ưu |
| **Tool Routing Accuracy** | **16 / 20 (80.0%)** | Model chọn tool khá nhạy |
| **Argument Accuracy** | **13 / 20 (65.0%)** | Sai sót tập trung ở tham số |
| **Multiturn Accuracy** | **4 / 6 (66.67%)** | Xử lý đa lượt cơ bản ổn |

- **Artifact Version:** `v0+peb1c8179815b+t5b22a2476d41`
- **Prompt Hash:** `eb1c8179815bd79d34de7d326420bb99b3072e6e8ae96464c02d4411f905fc68`
- **Tools Hash:** `5b22a2476d41b989d5dc1e54f24ce7890e781909deb2f7afafb856ab53a6d7c0`

---

## 3. Danh Sách Các Case FAIL Cần Bàn Giao Cho Đức & Phân Tích Nguyên Nhân

Trong 20 case, có **7 case bị FAIL**. Đây là bằng chứng thực tế từ file log để chuẩn bị tối ưu `v1`:

| Case ID | Loại test | Lỗi ghi nhận (`observed`) | Nguyên nhân cốt lõi trong Prompt/Tools gốc |
|---|---|---|---|
| **R03_web_news_routing** | Single-turn | `wrong_arg_value` | Query: *"Tin tức AI hôm nay có gì nổi bật?"*. Model gọi `lookup(query='AI')` nhưng **thiếu** `topic='news'` và `timeframe='day'` do mô tả của `lookup` trong `tools.yaml` chưa hướng dẫn quy ước các tham số này. |
| **R10_missing_handle** | Single-turn | `missing_tool_call` (`clarify`) | Query: *"Lấy các bài đăng gần đây của tài khoản này"*. Model tự tiện đoán một tài khoản ngẫu nhiên thay vì gọi `clarify` để hỏi người dùng. Lý do: `system_prompt.md` dòng 3 cố ý bảo bot *"do not ask them back — just make a sensible guess"*. |
| **R11_missing_url** | Single-turn | `missing_tool_call` (`clarify`) | Query: *"Đọc bài viết này giúp mình"*. Tương tự R10, model tự bịa URL để đọc thay vì gọi `clarify`. |
| **R12_confirm_before_send** | Single-turn | `wrong_arg_value` (`confirmed`) | Query: *"Gửi bản tin này lên kênh Telegram của team"*. Model gọi tool `send(confirmed=true)` gửi luôn mà không có sự xác nhận từ user. Lý do: `system_prompt.md` bảo bot *"just go ahead and do it so they don't have to wait"*. |
| **R13_parallel_web_and_tweets** | Single-turn | `missing_tool_call` | Query yêu cầu vừa tìm web vừa tìm tweet. Model chỉ gọi 1 tool duy nhất vì `system_prompt.md` có câu *"Always finish the request in a single step. Pick one tool"*. |
| **M02_carryover_timeframe** | Multi-turn | `wrong_arg_value` | Khi user bổ sung ngữ cảnh, model không kế thừa lại tham số `timeframe` từ lượt trước. |
| **M06_switch_tool** | Multi-turn | `missing_tool_call` / sai tool | Chuyển đổi giữa các tool trong chuỗi hội thoại chưa mượt. |

---

## 4. Hành Động Tiếp Theo Cho Các Thành Viên

### 📤 Bàn giao cho Đức (Nhánh `lab/eval`):
- Đọc file [runs/v0_B_base_gemini_20261110T104036405787.json](file:///c:/Users/buida/vinuni_day03_lab/K5-L3A-DAY03-GG-Prompt-Function-Calling-Tool-Design-MCP-/starter_v0/runs/v0_B_base_gemini_20261110T104036405787.json).
- Xác nhận lại 7 lỗi trên để đưa vào phân loại lỗi cho báo cáo Phần B.
- Bắt đầu thiết kế 10 eval cases trong [data/eval_group.json](file:///c:/Users/buida/vinuni_day03_lab/K5-L3A-DAY03-GG-Prompt-Function-Calling-Tool-Design-MCP-/starter_v0/data/eval_group.json) (5 single, 5 multi, có 1 case test `domain_summary`).

### 🛠️ Kế hoạch cho Quang (Bắt đầu `v1`):
- Đặt **Giả thuyết cho `v1`**: Loại bỏ thói quen đoán mò và ép 1 tool trong `system_prompt.md`, thêm quy tắc bắt buộc dùng `clarify` khi thiếu tên tài khoản (`screenname`) hoặc URL.
- Dự kiến sửa: [artifacts/system_prompt.md](file:///c:/Users/buida/vinuni_day03_lab/K5-L3A-DAY03-GG-Prompt-Function-Calling-Tool-Design-MCP-/starter_v0/artifacts/system_prompt.md).
- Chạy lại eval `v1` để đo lường mức độ cải thiện của `case_accuracy`.

### 💻 Bàn giao cho Đạt & Hùng:
- Hệ thống đã sẵn sàng, Đạt có thể pull code để bắt đầu tạo `tools/domain_summary/`.
- Hùng có thể dùng kết quả này để viết Phần A của báo cáo và test luồng trong `app.py`.

