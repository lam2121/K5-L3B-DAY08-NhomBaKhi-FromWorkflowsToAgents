# Báo cáo cá nhân — Nguyễn Trung Dũng

## 1. Thông tin thành viên

- Họ tên: Nguyễn Trung Dũng
- MSSV: 2A202604084
- Email: bomgoa102@gmail.com
- GitHub: bomgoa1102

## 2. Phần việc phụ trách

**Shape B — Single Agent (ReAct)** trong `src/lab8/shapes/single.py`. Shape xử lý yêu cầu hoàn phí bằng vòng lặp chọn công cụ đọc, sau đó chuyển khoản đề xuất cho host để kiểm tra và thực hiện hoàn tiền.

## 3. Đóng góp cụ thể

- Triển khai `run_claim()` và hàm `decide()` cho vòng ReAct, giới hạn tối đa 8 bước. Mỗi lần quyết định gọi MockLLM để mô phỏng và tính chi phí; các nhánh chọn công cụ trong phiên bản này được xác định bằng code, không do model sinh ra.
- Đọc claim, xác minh đơn hàng theo `principal_id`, đọc policy, tính bồi thường và tra cứu lịch sử hoàn tiền. Dữ liệu đơn hàng có cấu trúc được dùng để tính tiền thay vì tin nội dung ticket.
- Xử lý các trường hợp claim không tồn tại, thiếu mã đơn, không có quyền xem đơn, khoản bồi thường bằng 0 và kết quả host từ chối hoặc xung đột.
- Chạy vòng ReAct với `worker=True` để giới hạn quyền ghi của agent. Sau vòng lặp, chuyển **toàn bộ khoản đề xuất** cho `issue_refund()`; host chịu trách nhiệm kiểm tra approval, giới hạn hoàn tiền và ghi giao dịch.
- Truyền `crash_at` cho host, ghi trace khi có lỗi tại bước hoàn tiền và không chặn ngoại lệ crash. Đóng kết nối cơ sở dữ liệu trong `finally`.
- Ghi trace các bước và trạng thái cần thiết, tránh đưa ticket, dữ liệu thô và thông tin nhạy cảm vào trace.

Commit chính: [`1202bf65c7bd793aa2f8291ad69eaf9d52c395fa`](https://github.com/lam2121/K5-L3B-DAY08-NhomBaKhi-FromWorkflowsToAgents/commit/1202bf65c7bd793aa2f8291ad69eaf9d52c395fa) (`shape B`), thay đổi `src/lab8/shapes/single.py`. Commit này triển khai Shape B; test riêng được bổ sung sau commit.

### Test bổ sung

Commit [`2bd35df`](https://github.com/lam2121/K5-L3B-DAY08-NhomBaKhi-FromWorkflowsToAgents/commit/2bd35dfd1927793879f462f6cb7fdf49e94f3a96) (`add more test shape B`) bổ sung `src/tests/test_single_custom.py` với hai test:

- `test_single_unknown_claim_does_not_refund_and_writes_safe_trace`: kiểm tra claim không tồn tại trả về lỗi phù hợp, không tạo khoản hoàn tiền hoặc audit đã commit, và vẫn tạo trace JSON không chứa chuỗi secret mẫu. Test được Codex hỗ trợ tạo sau commit chính.
- `test_single_partial_refund_crash_then_replay_is_exactly_once`: kiểm tra trường hợp đơn đã được hoàn một phần, ticket chứa chỉ dẫn giả và secret; sau crash tại thời điểm đã ghi hoàn tiền nhưng chưa checkpoint, chạy lại vẫn chỉ có một giao dịch, đúng giới hạn hoàn tiền, tạo checkpoint và không lộ secret trong trace sau khi chạy lại. Test cũng kiểm tra Shape đề xuất toàn bộ 150.000 VND, còn host hoàn phần còn lại 120.000 VND.

## 4. Bằng chứng

- Mã nguồn và nội dung thay đổi: commit `1202bf65c7bd793aa2f8291ad69eaf9d52c395fa` ở trên.
- Chạy ma trận public dành riêng cho Shape B từ `src/`:

  ```bash
  python -m pytest -q -m student -o addopts= -k "single and not workflow and not orchestrator and not swarm"
  ```

  Kết quả kiểm tra trong môi trường dự án: **62 passed, 244 deselected**. Bộ này bao gồm các trường hợp public với nhiều seed, retry và crash; không thay thế kiểm thử hidden của giảng viên. Số deselected có thể thay đổi khi thêm test.
- Chạy test bổ sung: `python -m pytest -q tests/test_single_custom.py` — **2 passed**.
- Trước đó tôi đã chạy `python -m pytest -q -m student -o addopts= -k workflow` và nhận được `62 passed, 241 deselected`; kết quả đó thuộc Shape A, không dùng để chứng minh Shape B.

## 5. Công cụ AI đã dùng

Tôi dùng **Codex** để hỗ trợ viết code theo hướng vibe coding. Sau khi thành viên khác hoàn thành CP1, tôi tiếp tục thực hiện phần CP2 mà tôi phụ trách.

Ban đầu tôi đối chiếu kết quả test `-k workflow` với hướng dẫn của coach, nhưng lệnh này kiểm tra Shape A. Sau đó, với sự hỗ trợ của Codex, tôi chạy ma trận public riêng của Shape B và test bổ sung ở mục 4. Các kết quả này cung cấp bằng chứng trên các tình huống đã kiểm tra, nhưng không bảo đảm đúng cho mọi đầu vào. Tôi cần tiếp tục đọc code và tự giải thích các quyết định kỹ thuật.

## 6. Tự đánh giá

Phần triển khai Shape B đã có trong commit và vượt qua 62 kiểm thử public dành cho shape này; test bổ sung cũng chạy thành công. Tôi sử dụng Codex để hỗ trợ phát triển và kiểm thử, nên kết quả thể hiện phần việc đã thực hiện cùng AI, không có nghĩa là tôi đã tự viết hoặc hiểu đầy đủ toàn bộ code.

Những điểm cần nhiều thời gian tìm hiểu trong bài này gồm: hiểu luồng ReAct và ranh giới giữa agent chỉ đọc với host được phép ghi tiền; phân biệt số tiền đề xuất với số tiền host thực sự được hoàn; và kiểm tra retry/crash để tránh hoàn trùng. Ở phần test, việc chọn đúng shape, tạo dữ liệu kiểm thử và kiểm tra cả trạng thái lẫn tác động trên ledger khó hơn chỉ nhìn số bài pass. Việc dùng Codex vẫn đòi hỏi đọc yêu cầu, đặt câu hỏi và kiểm chứng kết quả; tôi chưa thể khẳng định đã nắm vững tất cả các điểm này.

Tôi cần tiếp tục đọc code, tự giải thích luồng xử lý, bổ sung các tình huống biên và chạy lại test sau mỗi thay đổi. Kết quả public chưa thay thế bộ hidden và không chứng minh hệ thống đúng trong mọi trường hợp.
