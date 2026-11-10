# Ghi chú kiểm thử Research Agent

Nhập từng câu vào ô Trò chuyện để kiểm tra agent. Với các trường hợp độc lập, bắt đầu hội thoại mới. Các kết quả dưới đây là kỳ vọng kiểm thử.

| Công cụ | Câu nhập | Hành vi cần quan sát |
| --- | --- | --- |
| Tra cứu tin tức | Tin tức AI nổi bật trong tuần này là gì? | Gọi `lookup` với chủ đề tin tức và phạm vi một tuần. |
| Đọc trang web | Đọc và tóm tắt nội dung trang https://openai.com/research/ | Gọi `fetch` với URL đã nhập. |
| Bài đăng theo tài khoản | Xem các bài tweet mới nhất của Sam Altman (@sama) | Gọi `timeline` với tài khoản `sama`. |
| Tìm thảo luận trên X | Tìm các bài đăng nổi bật nhất (Top) trên X bàn về AI Agent | Gọi `social_search` với kiểu tìm kiếm `Top`. |
| Tra cứu chính sách | Quy định nội bộ về trích dẫn nguồn (source citation) là gì? | Gọi `policy` để tìm quy định về trích dẫn nguồn. |
| Tìm bài báo | Tìm các bài báo trên arXiv về chủ đề RAG evaluation | Gọi `papers` với chủ đề đã nhập. |
| Xác nhận Telegram | Hãy đăng bản tin 'AI Digest hôm nay' lên kênh Telegram ngay | Agent phải yêu cầu xác nhận trước khi đăng. Dừng ở bước yêu cầu xác nhận. |

## Kiểm thử hỏi lại và nối ngữ cảnh

1. Nhập “Cho tôi xem các bài tweet gần đây của tài khoản đó”. Agent cần hỏi lại tài khoản X qua `clarify`.
2. Trong cùng hội thoại, nhập “Tài khoản của Sam Altman (@sama)”. Agent cần dùng thông tin vừa bổ sung để gọi `timeline` cho tài khoản `sama`.
