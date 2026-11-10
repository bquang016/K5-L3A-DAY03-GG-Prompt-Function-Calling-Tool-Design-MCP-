# Day 03 Lab v2 Report — Research Agent

> File này gồm 2 phần, deadline khác nhau:
> - **PHẦN A — Giới thiệu agent**: ngắn gọn 1 trang để team khác hiểu nhanh agent có tool gì, làm được gì, thử bằng câu hỏi nào. **Xong trước 16:30** để làm tài liệu phụ trợ khi demo. Có thể làm thành poster HTML/SVG (`artifacts/poster.html` / `poster.svg`) để show cho team cùng zone.
> - **PHẦN B — Chi tiết / Bằng chứng**: bảng đầy đủ (v0–v3, failure, eval, chat) dựa trên log thật. **Có thể hoàn thiện sau buổi debate để nộp bài.**

## Team

- Team: Research Agent Studio Team
- Members: Quang, Đạt, Đức, Hùng
- Provider/model: Gemini / `gemini-3.5-flash-lite`

---

# PHẦN A — Giới thiệu agent

## A1. Agent này làm được gì

Research Agent đa năng chuyên sâu: Tự động tra cứu tin tức thời sự trên web internet qua Tavily, tìm kiếm và trích xuất tweet từ mạng xã hội X/Twitter, đọc toàn văn nội dung trang web từ link URL qua Firecrawl, phân tích và thống kê số lượng nguồn theo từng tên miền website (`domain_summary`), tra cứu chính sách công ty nội bộ và bài báo khoa học arXiv, định dạng bản tin digest Markdown và có cơ chế bảo vệ (guardrail) bắt buộc xác nhận của người dùng trước khi gửi tin lên kênh Telegram.

**Link dùng thử (deploy):**

> Dán link public để team khác mở thử ngay. Cách deploy nhanh bằng Cloudflare Tunnel xem README: `cloudflared tunnel --url http://localhost:8501`.
>
> URL: http://localhost:8501 (hoặc link Cloudflare Tunnel khi expose)

## A2. Tool agent có

| Tên tool | Làm được gì | Tool mới nhóm thêm? |
|---|---|---|
| `clarify` | Hỏi lại người dùng khi thiếu thông tin hoặc cần xác nhận trước hành động ghi | Không |
| `lookup` | Tra cứu thông tin và tin tức thời sự trên web internet qua Tavily API | Không |
| `fetch` | Đọc và trích xuất toàn văn nội dung trang web từ một URL qua Firecrawl | Không |
| `timeline` | Lấy các bài đăng/tweet gần đây của một tài khoản Twitter cụ thể | Không |
| `social_search` | Tìm kiếm bài đăng/tweet trên Twitter theo từ khóa hoặc chủ đề | Không |
| `domain_summary` | Đếm và nhóm số lượng URL theo từng tên miền từ danh sách các đường link nguồn | **CÓ (Tool mới của nhóm)** |
| `format` | Định dạng dữ liệu đã thu thập thành bản tin tổng hợp Markdown Digest | Không |
| `send` | Gửi tin nhắn lên kênh Telegram bên ngoài khi đã được người dùng xác nhận | Không |
| `policy` | Tra cứu quy định, chính sách nội bộ của công ty | Không |
| `papers` | Tìm kiếm bài báo khoa học học thuật trên arXiv | Không |
| `paper_text` | Tải và trích xuất text từ file PDF bài báo arXiv | Không |

## A3. Câu hỏi mẫu để thử

1. "Tin tức AI hôm nay có gì nổi bật trên web?" *(Thử khả năng tra cứu tin tức thời sự qua `lookup`)*
2. "Tweet mới nhất của Sam Altman là gì?" *(Thử khả năng map tên sang handle `sama` và lấy tweet qua `timeline`)*
3. "Đếm số nguồn theo tên miền từ các URL sau: https://openai.com/research, https://google.com/search, https://openai.com/blog" *(Thử tool mới `domain_summary` do nhóm tự phát triển!)*
4. "Tóm tắt bài viết này giúp mình" *(Thử tính năng an toàn: bot không tự tiện đoán mò mà gọi `clarify` hỏi URL)*
5. "Gửi bản tin tổng hợp AI lên kênh Telegram của team" *(Thử guardrail an toàn: bot hỏi xác nhận yes/no trước khi gửi tin)*

---

# PHẦN B — Chi tiết / Bằng chứng

## B1. Version Evidence

Fill from `artifacts/version_log.csv` and `runs/*.json`.

| Version | Changed Artifact | Hypothesis | Metric Before | Metric After | Run File |
|---|---|---|---:|---:|---|
| v0 | baseline | starter baseline with deliberate flaws (guessing instead of clarify, immediate send) | N/A | 65.0% | `runs/v0_B_base_gemini_20261110T104036405787.json` |
| v1 | `artifacts/system_prompt.md` | fix guessing and single-step bias, remove bad instructions and enforce clarify/parallel rules | 65.0% | 76.5% | `runs/v1_B_base_gemini_20261110T104451079167.json` |
| v2 | `artifacts/tools.yaml` | specify tool boundaries and required params, clarify parameter requirements and acronym preservation | 76.5% | 95.0% | `runs/v2_B_base_gemini_20261110T104952520561.json` |
| v3 | integrated `domain_summary` | integrate new tool while maintaining 100% routing accuracy | 95.0% | 95.0% (100% routing) | `runs/v3_B_base_gemini_20261110T112600283045.json` |

## B2. Failure Analysis

Use actual failures from `results[*].result.failures`.

| Case ID | Failure Type | Actual Tool Calls | What Failed | Fix |
|---|---|---|---|---|
| R03 | wrong_arg_value | `lookup(query="AI news today", topic="news", timeframe="day")` | Query thừa chữ "news today" thay vì chỉ giữ từ khóa cốt lõi "AI" | Chuẩn hóa quy tắc trích xuất từ khóa cốt lõi, cấm lặp lại các từ chỉ thời gian hay thể loại vào query. |
| R10 | missing_info | `timeline(screenname="sama")` | Tự đoán mò handle `sama` khi người dùng chỉ yêu cầu xem tweet mới nhất | Bổ sung quy tắc: nếu người dùng không cung cấp tài khoản, bắt buộc gọi `clarify(response_type="text")`. |
| R11 | missing_info | `lookup(query="tin tức nổi bật hôm nay")` | Tự đoán mò ý định và gọi sai tool khi người dùng yêu cầu tóm tắt nhưng không có URL | Bổ sung quy tắc: thiếu URL khi tóm tắt bài viết bắt buộc phải gọi `clarify` để hỏi link. |
| R12 | wrong_boundary | `send(confirmed=true, text="...")` | Tự ý gửi tin nhắn ra bên ngoài và tự bịa nội dung khi chưa có xác nhận | Thiết lập guardrail bắt buộc gọi `clarify(response_type="yes_no")` để người dùng xác nhận trước khi gọi `send`. |
| R13 | wrong_tool + wrong_arg_value | `lookup(query="AI news today")` | Thiếu tool `social_search` và query thừa từ khi người dùng hỏi cả web và mạng xã hội | Bổ sung quy định gọi multi-tool song song khi yêu cầu bao gồm nhiều nguồn. |
| M02 | wrong_arg_value | `lookup(query="tin tức robotics hôm nay AI robot")` | Bị nhiễm ngữ cảnh từ lượt trước (lẫn từ "AI" dù lượt hiện tại chỉ yêu cầu robotics) | Cập nhật hướng dẫn: ưu tiên tuyệt đối yêu cầu ở lượt hiện tại, loại bỏ ngữ cảnh đã bị người dùng sửa. |
| M06 | wrong_arg_value | `lookup(query="OpenAI news", timeframe="week")` | Thừa từ "news" và tự động gán timeframe="week" khi không có yêu cầu | Không thêm từ thừa vào query và để timeframe mặc định khi không xác định. |

## B3. Team Eval Cases

List the 10 cases added to `data/eval_group.json` (5 single turn + 5 multi turn).

| Case ID | What It Tests | Expected Tool/Behavior | Result |
|---|---|---|---|
| G01_missing_handle_pronoun | Người dùng dùng đại từ "anh ấy" không rõ danh tính | `clarify(response_type="text")` | PASS |
| G02_confirm_send_with_text | Có sẵn nội dung nhưng chưa có sự xác nhận gửi của người dùng | `clarify(response_type="yes_no")` | PASS |
| G03_news_month_short_query | Lọc tin theo tháng với query ngắn gọn, không thừa từ | `lookup(query="Nvidia", topic="news", timeframe="month")` | PASS |
| G04_domain_summary_count | Thống kê số lượng URL theo từng tên miền | `domain_summary(urls=[...])` | PASS |
| G05_thanks_no_tool | Câu cảm ơn xã giao ngoài phạm vi tra cứu | `no_tool: true` (trả lời trực tiếp) | PASS |
| GM01_confirm_then_send | Đa lượt: đưa nội dung -> người dùng chốt "Ok, gửi đi" rõ ràng | `send(confirmed=true)` | PASS |
| GM02_clarify_name_to_handle | Đa lượt: hỏi tweet -> user đưa tên Yann LeCun -> map thành `ylecun` và chốt limit=7 | `timeline(screenname="ylecun", limit=7)` | PASS |
| GM03_multiturn_domain_summary | Đa lượt: gom link qua 2 lượt đầu -> lượt 3 yêu cầu đếm theo tên miền | `domain_summary(urls=[3 links])` | PASS |
| GM04_correct_timeframe_day_to_month | Đa lượt: đính chính từ "hôm nay" sang "trong tháng này" và chỉ lấy "Tesla" | `lookup(query="Tesla", topic="news", timeframe="month")` | PASS |
| GM05_out_of_scope_after_research | Đa lượt: sau khi tra cứu tin AI, lượt cuối yêu cầu viết hàm code Python | `no_tool: true` (từ chối lịch sự, không gọi tool) | PASS |

> Kết quả chạy eval bộ Group trên v3 (`runs/v3_B_group_gemini_20261110T121955980021.json`): **10/10 PASS (100% accuracy, 100% routing, 100% multiturn)**.

## B4. Live Chat Evidence

Use `transcripts/*.transcript.json`.

Transcript file: `transcripts/v3_gemini_20261110T122042024241.transcript.json`

| Turn | User Request | Tool Calls | Version Evidence | Outcome |
|---|---|---|---|---|
| 1 | "Tin tức AI hôm nay" | `lookup(query="AI", timeframe="day", topic="news")`<br>`format(template="sections", ...)` | `v3+p876040c16a28+tb74750c49704` | Agent tra cứu tin tức thời sự trong ngày, tự động gom nhóm và định dạng Markdown Digest có trích dẫn nguồn đầy đủ. |
| 2 | "Thống kê các tên miền sau: https://openai.com/blog, https://google.com/ai, https://openai.com/research" | `domain_summary(urls=[...])` | `v3+p876040c16a28+tb74750c49704` | Agent gọi đúng tool mới `domain_summary`, trả về bảng thống kê chi tiết: openai.com (2 URLs), google.com (1 URL). |
| 3 | "Cảm ơn bạn nhé" | *(Không gọi tool nào)* | `v3+p876040c16a28+tb74750c49704` | Agent nhận diện câu xã giao kết thúc hội thoại, trả lời lịch sự và thân thiện mà không gọi tool dư thừa. |

## B5. Bonus Evidence

Only fill if your team did bonus.

| Bonus | Evidence File | What Worked | Risk / Guardrail |
|---|---|---|---|
| send (Telegram) | `tests/test_tools_todo.py`, `data/eval_group.json` (G02, GM01) | Bắt buộc xin xác nhận trước khi thực hiện hành động ghi (write action), chỉ gửi khi `confirmed=true` | Tránh việc agent tự ý gửi tin rác hoặc nội dung chưa được kiểm duyệt lên kênh Telegram. |
| arXiv/company policy | `tests/test_tools_todo.py` | Lọc dữ liệu độc hại vào `untrusted_text`, phân tách rõ ràng với dữ liệu tin cậy (`facts`) | Chống prompt injection từ tài liệu bên ngoài hoặc văn bản chính sách chưa được xác thực. |
| UI | `app.py`, `transcripts/*.transcript.json` | Giao diện Streamlit hiện đại, realtime badge, fallback Gemini thông minh, hiển thị tiến trình gọi tool trực quan | Cung cấp link trực quan để người dùng và các team khác trải nghiệm trực tiếp. |
| Tool unit tests (`tests/`) | `pytest tests/ -v` (92 passed) | Toàn bộ 92 tests đều xanh 100% (0 fail, 0 skip), bao gồm contract tests, test cho tool mới `domain_summary` | Đảm bảo tính nhất quán tuyệt đối giữa mã nguồn, schema `tools.yaml` và dữ liệu đánh giá. |
