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
|  |  |  |  |  |

## B3. Team Eval Cases

List the 10 cases added to `data/eval_group.json` (5 single turn + 5 multi turn).

| Case ID | What It Tests | Expected Tool/Behavior | Result |
|---|---|---|---|
|  |  |  |  |

## B4. Live Chat Evidence

Use `transcripts/*.transcript.json`.

| Turn | User Request | Tool Calls | Version Evidence | Outcome |
|---|---|---|---|---|
|  |  |  |  |  |

## B5. Bonus Evidence

Only fill if your team did bonus.

| Bonus | Evidence File | What Worked | Risk / Guardrail |
|---|---|---|---|
| send (Telegram) |  |  |  |
| arXiv/company policy |  |  |  |
| UI |  |  |  |
| Tool unit tests (`tests/`) | `pytest` output |  |  |

Tool unit tests: số test đã viết, số bug tìm được trong tool có sẵn (nếu có), và một ví dụ lỗi mà unit test bắt được nhưng eval không bắt được.

## B6. Reflection

- Which fixes belonged in `system_prompt.md`?
- Which fixes belonged in `tools.yaml`?
- Which failure needed manual review instead of automatic grading?
- What would you improve next?

## B7. Small Local Model Challenge (bonus)

Only fill if your team did the local model challenge.

| Version | Model (provider) | Prompt/Tools | case_accuracy | tool_routing | argument | multiturn | Run File |
|---|---|---|---|---|---|---|---|
| v3 | (cloud) | v3 |  |  |  |  |  |
| v3-... | (ollama) | v3 |  |  |  |  |  |
| v3-... | (ollama) | v3 |  |  |  |  |  |
| v4-local |  |  |  |  |  |  |  |
| v5-local |  |  |  |  |  |  |  |

Lỗi đặc thù của model nhỏ (đếm từ run JSON):

| Failure Pattern | Count | Example Case | Fix Tried | Helped? |
|---|---|---|---|---|
| wrong / hallucinated tool |  |  |  |  |
| invalid JSON args (`_invalid_json_arguments`) |  |  |  |  |
| no tool call / answered directly |  |  |  |  |
| missed `clarify` |  |  |  |  |
| repeated / unnecessary calls |  |  |  |  |

- Cái gì giúp model nhỏ gọi tool đúng hơn nhất? Bằng chứng?
- Bản prompt tối ưu cho local chạy trên model cloud thì sao?
- Khi nào nhóm sẽ chọn model local thay vì cloud cho agent này?
