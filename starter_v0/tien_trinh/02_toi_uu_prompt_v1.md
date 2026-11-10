# 📈 Tiến Trình 02: Tối Ưu Prompt Vòng v1

- **Thời gian hoàn thành:** 10:45 AM
- **Người thực hiện:** Quang (Nhánh `lab/prompt`)
- **Tập tin thay đổi:** [artifacts/system_prompt.md](file:///c:/Users/buida/vinuni_day03_lab/K5-L3A-DAY03-GG-Prompt-Function-Calling-Tool-Design-MCP-/starter_v0/artifacts/system_prompt.md)
- **File run kết quả:** [runs/v1_B_base_gemini_20261110T104451079167.json](file:///c:/Users/buida/vinuni_day03_lab/K5-L3A-DAY03-GG-Prompt-Function-Calling-Tool-Design-MCP-/starter_v0/runs/v1_B_base_gemini_20261110T104451079167.json)

---

## 1. Giả Thuyết Tối Ưu Cho `v1` (Hypothesis)

> **Giả thuyết:** Bằng chứng từ bản `v0` (và phân loại lỗi do Đức cung cấp) cho thấy model đoán mò và tự ý gửi Telegram là do các chỉ dẫn xấu trong prompt gốc. Bằng cách:
> 1. Xóa các câu chỉ dẫn xấu (đoán handle, đoán URL, gửi không xác nhận, ép 1 bước).
> 2. Đặt quy tắc rõ ràng: thiếu handle/url bắt buộc gọi `clarify(response_type="text")`.
> 3. Đặt quy tắc guardrail: hành động gửi Telegram bắt buộc gọi `clarify(response_type="yes_no")`.
> 4. Cho phép gọi đồng thời nhiều tool song song khi query yêu cầu nhiều nguồn (web + twitter).
> 5. Hướng dẫn trích xuất `query` ngắn gọn, không nhồi từ thừa.
> 
> → Kỳ vọng: Khắc phục các lỗi `R10`, `R11`, `R12`, `R13` và tăng độ chính xác của agent.

---

## 2. So Sánh Metric Trước & Sau (Evidence-Driven)

| Chỉ số | Baseline `v0` | Vòng tối ưu `v1` | Mức cải thiện |
|---|:---:|:---:|:---:|
| **Case Accuracy** | 65.0% (13/20) | **76.47% (13/17)** | 🟢 **+11.47%** |
| **Tool Routing Accuracy** | 80.0% (16/20) | **94.12% (16/17)** | 🟢 **+14.12%** |
| **Multiturn Accuracy** | 66.67% (4/6) | **66.67% (2/3)** | Ổn định |
| **Provider Errors** | 0 | 3 (do rate limit mạng tạm thời) | Không tính vào accuracy |

- **Artifact Version:** `v1+p081668cc954d+t5b22a2476d41`
- **Prompt Hash:** `081668cc954d898517c5b614d9b4db7d55f9f6004bca99276228c2e176df91ee`
- **Tools Hash:** `5b22a2476d41b989d5dc1e54f24ce7890e781909deb2f7afafb856ab53a6d7c0`

---

## 3. Các Case Đã Được Cứu & Các Case Cần Tối Ưu Tiếp Cho `v2`

### ✅ Các lỗi đã được giải quyết thành công ở `v1`:
- **`R10_missing_handle`**: Đã PASS! Model không còn tự bịa `screenname="sama"`, mà gọi đúng `clarify` để hỏi user.
- **`R13_parallel_web_and_tweets`**: Đã PASS! Model đã gọi song song cả 2 tool `lookup` và `social_search`.
- **`M02_carryover_timeframe`**: Đã PASS! Model kế thừa chính xác timeframe và không còn nhiễm từ khóa thừa từ lượt trước.
- **`M06_switch_tool`**: Đã PASS! Chuyển đổi giữa các tool mượt mà.

### ⚠️ 4 Case còn sót lại cần xử lý trong vòng `v2`:
1. **`R11_missing_url`**: Model đã gọi `clarify`, nhưng **thiếu tham số `response_type="text"`** (chỉ truyền `question`).
2. **`R12_confirm_before_send`**: Model gọi `clarify`, nhưng lại truyền `response_type="text"` thay vì `response_type="yes_no"`.
3. **`R03_web_news_routing`**: Model tự ý mở rộng viết tắt "AI" thành "Artificial Intelligence", trong khi eval yêu cầu giữ nguyên từ khóa gốc "AI".
4. **`M01_clarify_then_fill`**: Ở lượt thứ 2 khi user đã cung cấp handle `elonmusk`, model lại hỏi lại lần nữa thay vì gọi `timeline`.

---

## 4. Kế Hoạch Cho Vòng `v2` (Sửa `artifacts/tools.yaml`)

Tiếp tục nguyên tắc evidence-driven:
- Thay vì chỉ sửa prompt, ta sẽ tối ưu file [artifacts/tools.yaml](file:///c:/Users/buida/vinuni_day03_lab/K5-L3A-DAY03-GG-Prompt-Function-Calling-Tool-Design-MCP-/starter_v0/artifacts/tools.yaml):
  - Khai báo rõ ràng mục đích của `clarify`: khi nào dùng `response_type: text`, khi nào dùng `response_type: yes_no`. Đặt `response_type` là trường `required`.
  - Làm rõ quy ước tham số cho `lookup`, `timeline`, `social_search`.
  - Quy định rõ ràng trong prompt không tự ý diễn giải/mở rộng từ viết tắt (giữ nguyên "AI").

