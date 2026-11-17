# Báo cáo cá nhân — Đặng Nguyễn Nhật Minh

## 1. Thông tin thành viên

- Họ tên: Đặng Nguyễn Nhật Minh
- MSSV: 2A202604118
- Email: 26ai.minhdnn@vinuni.edu.vn
- GitHub: MN-HD

## 2. Phần việc phụ trách

**Shape A — Deterministic Workflow (Quy trình xử lý tất định)**

Tôi phụ trách triển khai Shape A, kiến trúc xử lý claim hoàn phí vận chuyển theo một quy trình cố định bằng Python, tại file `src/lab8/shapes/workflow.py`.

Mục tiêu của phần việc là xây dựng một quy trình xử lý hoàn phí có tính xác định, trong đó các quyết định nghiệp vụ quan trọng được thực hiện bằng code thay vì phụ thuộc vào khả năng suy luận của mô hình ngôn ngữ.

Các nhiệm vụ chính bao gồm:

- Tiếp nhận và truy xuất thông tin claim thông qua các hàm đọc dữ liệu an toàn có sẵn.
- Kiểm tra sự tồn tại của đơn hàng và quyền sở hữu đơn hàng của khách hàng.
- Tính toán mức bồi thường dựa trên dữ liệu đơn hàng có cấu trúc và chính sách hiện hành.
- Gửi yêu cầu hoàn tiền đến lớp host để kiểm tra phê duyệt và thực hiện giao dịch.
- Xử lý các trường hợp thiếu thông tin, đơn hàng không hợp lệ, yêu cầu bị từ chối và yêu cầu được chấp thuận.
- Đảm bảo tính an toàn khi retry và phục hồi sau crash.
- Tạo trace hợp lệ mà không làm lộ thông tin nhạy cảm của khách hàng.

## 3. Đóng góp cụ thể

### 3.1. Triển khai Shape A

Hoàn thiện phần triển khai tại:

`src/lab8/shapes/workflow.py`

Quy trình được triển khai theo các bước tuần tự:

1. Khởi tạo kết nối cơ sở dữ liệu, budget, run ID và trace.
2. Truy xuất claim bằng `get_claim_view()`.
3. Kiểm tra claim có tồn tại và có mã đơn hàng hay không.
4. Xác minh quyền sở hữu đơn hàng thông qua `lookup_order()`.
5. Tính toán mức bồi thường bằng `compute_compensation()`.
6. Gửi toàn bộ mức bồi thường đề xuất đến `durability.issue_refund()`.
7. Xử lý kết quả kiểm tra phê duyệt, xung đột số tiền và hoàn tiền thành công.
8. Trả về kết quả thông qua `finish()` và đóng kết nối cơ sở dữ liệu.

### 3.2. Các quyết định kỹ thuật quan trọng

Trong quá trình triển khai, tôi tập trung vào các nguyên tắc sau:

- **Xử lý tất định:** Không sử dụng LLM để tự quyết định số tiền hoàn phí hoặc xác định quyền được bồi thường. Các quyết định này được thực hiện bằng code Python và các hàm nghiệp vụ có sẵn.
- **Ưu tiên dữ liệu đáng tin cậy:** Sử dụng dữ liệu đơn hàng có cấu trúc thay vì tin vào những thông tin do khách hàng tự khai trong nội dung ticket.
- **Phân chia trách nhiệm giữa Shape và Host:** Shape tính toán mức bồi thường đề xuất, còn host chịu trách nhiệm xác minh approval, áp dụng giới hạn hoàn tiền theo đơn hàng, chống ghi trùng và thực hiện transaction.
- **Đảm bảo an toàn khi retry và crash:** Truyền tham số `crash_at` vào `issue_refund()` và không bắt hoặc che giấu ngoại lệ `InjectedCrash`, để cơ chế phục hồi của host hoạt động đúng.
- **Quản lý kết nối:** Sử dụng `finally` để đảm bảo kết nối cơ sở dữ liệu luôn được đóng.
- **Bảo mật trace:** Chỉ ghi các thông tin cần thiết cho việc theo dõi quá trình xử lý; không ghi nguyên dữ liệu claim, nội dung ticket hoặc thông tin nhạy cảm vào trace.

Một điểm kỹ thuật quan trọng là phải truyền toàn bộ mức bồi thường đề xuất vào `issue_refund()`, thay vì tự tính phần tiền còn được hoàn sau các giao dịch trước đó. Việc áp dụng giới hạn hoàn tiền và tính toán số tiền thực tế thuộc trách nhiệm của host.

### 3.3. Bổ sung kiểm thử

Tạo file kiểm thử mới:

`src/tests/test_workflow.py`

Bổ sung test:

`test_unknown_claim_fails_without_refund_and_writes_clean_trace`

Test này kiểm tra cách Shape A xử lý một claim không tồn tại, cụ thể:

- Trả về trạng thái `failed`.
- Có `error_reason` là `unknown_claim`.
- `proposal_amount` bằng 0.
- Không phát sinh lời gọi LLM hoặc refund effect.
- Không tạo bản ghi hoàn tiền hoặc audit đã commit.
- Vẫn tạo được trace JSON hợp lệ và mới.
- Không để lộ chuỗi secret `CANARY_SECRET_*` trong trace.

### 3.4. Commit kỹ thuật chính

- Commit hash: `ffa17da`
- Commit message: `Implement deterministic Shape A workflow`
- Các file được thay đổi:
  - `src/lab8/shapes/workflow.py`
  - `src/tests/test_workflow.py`

## 4. Bằng chứng

### 4.1. Đóng góp trên GitHub

Commit triển khai chính:

https://github.com/lam2121/K5-L3B-DAY08-NhomBaKhi-FromWorkflowsToAgents/commit/ffa17da

### 4.2. Chạy thử quy trình xử lý thực tế

Đã kiểm tra triển khai bằng claim `C-001`, seed `11`.

- Run ID: `R-workflow-C-001-s11`
- Trạng thái: `resolved`
- Số tiền đề xuất: 35.000 VND
- Số tiền thực tế được hoàn: 35.000 VND
- Số audit `refund_committed`: 1
- Số lần gọi model: 0
- Số lần gọi tool: 3
- Chi phí mô phỏng: 30 VND
- Trace được tạo thành công.

### 4.3. Kết quả kiểm thử

| Nội dung kiểm tra | Kết quả |
|---|---|
| Biên dịch Python (`py_compile`) | Thành công |
| Smoke test | Passed |
| Bộ test mặc định | 55 passed |
| Bộ 62 test của Shape A | 62 passed |
| Test bổ sung do cá nhân viết | 1 passed |
| Crash safety suite của host và swarm tham chiếu | 20/20 |

Ngoài ra, khả năng retry và phục hồi crash của Shape A được kiểm tra trực tiếp thông qua T11 và T12 trong bộ 62 student tests.

Các kết quả trên được lấy từ quá trình thực thi lệnh kiểm thử trên môi trường phát triển, không chỉnh sửa thủ công kết quả hoặc số liệu kiểm thử.

## 5. Công cụ AI đã sử dụng

Tôi sử dụng **ChatGPT (OpenAI)** làm công cụ hỗ trợ trong quá trình tìm hiểu, triển khai và kiểm thử bài tập.

Các mục đích sử dụng chính:

- Giải thích yêu cầu của đề bài và trách nhiệm của Shape A.
- Hỗ trợ tìm hiểu kiến trúc repository và vai trò của các module Python có sẵn.
- Gợi ý cấu trúc triển khai và mã nguồn Python cho deterministic workflow.
- Hỗ trợ xây dựng test bổ sung cho trường hợp claim không tồn tại và kiểm tra bảo mật trace.
- Hướng dẫn cấu hình môi trường Python, thực hiện kiểm thử bằng pytest và thao tác Git.
- Giải thích kết quả kiểm thử, hỗ trợ xử lý việc đồng bộ code khi thành viên khác cập nhật repository.

### Cách kiểm tra kết quả do AI hỗ trợ

Tôi không mặc định các gợi ý của AI là chính xác mà tiến hành kiểm tra bằng các tài liệu, code và công cụ có sẵn trong repository.

Các bước kiểm chứng bao gồm:

- Đọc và kiểm tra những module liên quan đến workflow, compensation, durability, trace và schema.
- Biên dịch file Python để phát hiện lỗi cú pháp.
- Chạy thử một claim có dữ liệu mẫu và kiểm tra kết quả hoàn tiền thực tế.
- Chạy toàn bộ bộ test mặc định.
- Chạy đầy đủ 62 test của Shape A.
- Chạy test bổ sung do cá nhân viết.
- Chạy crash safety suite để kiểm tra tính an toàn của host.
- Kiểm tra các file được stage và commit trước khi push lên GitHub.
- Đồng bộ với commit mới nhất của nhóm trước khi đưa đóng góp cá nhân lên nhánh chung.

ChatGPT được sử dụng như công cụ hỗ trợ phát triển và giải thích kỹ thuật; kết quả cuối cùng được kiểm chứng thông qua việc thực thi code và các bài kiểm thử thực tế.

## 6. Tự đánh giá

Tôi đã hoàn thành nhiệm vụ được phân công là triển khai Shape A và bổ sung một test riêng vào repository của nhóm.

Qua bài tập này, tôi hiểu rõ hơn về kiến trúc deterministic workflow và tầm quan trọng của việc phân chia trách nhiệm giữa code xử lý nghiệp vụ, mô hình ngôn ngữ và lớp host quản lý các thao tác có tác động đến dữ liệu.

Một trong những kiến thức quan trọng nhất tôi học được là sự khác biệt giữa việc tính toán mức bồi thường và việc thực sự phê duyệt, ghi nhận khoản hoàn tiền. Workflow chỉ đề xuất mức bồi thường dựa trên dữ liệu đáng tin cậy; host mới là thành phần xác minh approval, áp dụng giới hạn hoàn tiền và thực hiện transaction.

Tôi cũng hiểu rõ hơn về idempotency, crash recovery, quản lý transaction trong SQLite và yêu cầu bảo mật đối với trace.

Mặc dù có sử dụng ChatGPT để hỗ trợ quá trình triển khai và kiểm thử, tôi đã trực tiếp thực hiện các bước kiểm tra code và xác minh kết quả bằng bộ test của repository.

Nhìn chung, tôi đánh giá đã hoàn thành tốt phần việc được giao. Trong những bài tập tiếp theo, tôi muốn tiếp tục cải thiện khả năng tự thiết kế và triển khai các hệ thống xử lý có độ tin cậy cao, đặc biệt là những vấn đề liên quan đến transaction, tính nhất quán dữ liệu và phục hồi sau lỗi.