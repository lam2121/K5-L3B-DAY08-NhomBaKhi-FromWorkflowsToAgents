# Báo cáo cá nhân — Nguyễn Duy Hưng

## 1. Thông tin thành viên

- Họ tên: Nguyễn Duy Hưng
- MSSV: 2A202604110
- Email:  26ai.hungnd6@vinuni.edu.vn
- GitHub: Hungnd1208

## 2. Phần việc phụ trách

**Shape C — Orchestrator & Read-only Investigators (Kiến trúc Điều phối & Điều tra viên chỉ đọc)**

Tôi phụ trách triển khai Shape C, kiến trúc xử lý claim hoàn phí vận chuyển theo mô hình Orchestrator - Worker tại file `src/lab8/shapes/orchestrator.py`, cùng các bài kiểm thử xác thực ranh giới bảo mật và tính an toàn của handoff.

Mục tiêu chính của Shape C là thiết lập sự phân tách rõ ràng giữa thành phần lập kế hoạch/quyết định cấp cao (Orchestrator) và các tác tử thu thập dữ kiện (Investigators), đảm bảo tính an toàn dữ liệu và tuân thủ ranh giới thẩm quyền:

- **Phân tách thẩm quyền:** Investigators hoàn toàn ở chế độ chỉ đọc (`worker=True`), bị từ chối mọi thao tác ghi cơ sở dữ liệu (`WRITE_TOOLS`).
- **Ranh giới bảo mật (Handoff Sanitization):** Gói dữ liệu chuyển giao (`handoff.v1`) chỉ chứa các trường trong allowlist. Tuyệt đối không chuyển giao `parent_secret`, raw headers, hoặc toàn bộ dòng claim thô sang cho investigator.
- **Tuân thủ quy tắc nghiệp vụ:** Bỏ qua các thông tin người dùng tự khai trong ticket; chỉ căn cứ vào dữ liệu xác minh từ database đơn hàng và policy hiện hành.
- **Thẩm quyền hoàn tiền tập trung:** Toàn bộ quyền duyệt và ghi tiền do Host kiểm soát; Orchestrator đề xuất mức hoàn đầy đủ (`full quote`) và chuyển sang `durability.issue_refund()`.
- **An toàn khi crash và idempotency:** Chuyển tiếp tham số `crash_at` để host kích hoạt cơ chế mô phỏng sự cố và ghi nhận trace sạch sẽ.

## 3. Đóng góp cụ thể

### 3.1. Triển khai Shape C

Hoàn thiện triển khai kiến trúc Orchestrator tại:

`src/lab8/shapes/orchestrator.py`

Quy trình xử lý gồm các bước chuẩn hóa:

1. **Khởi tạo và tra cứu ban đầu:** Mở kết nối SQLite an toàn, khởi tạo `Budget` để ghi nhận token/chi phí, sinh `run_id` duy nhất và khởi tạo `Trace`. Đọc dữ liệu claim thông qua hàm bọc an toàn `get_claim_view()` (thay vì truy vấn trực tiếp bảng SQLite).
2. **Lập kế hoạch (Planning):** Gọi MockLLM với mục đích `purpose="plan"` để phân tích nội dung khiếu nại.
3. **Xử lý dừng sớm:** Kiểm tra nếu thiếu `order_id` thì dừng sớm ngay lập tức với trạng thái `needs_info`, số tiền đề xuất là `0`, không gọi công cụ ghi hoặc chuyển giao handoff không cần thiết.
4. **Đóng gói Handoff an toàn:** Sử dụng `lab8.handoff.make_handoff` với danh sách công cụ được phép đọc: `["lookup_order", "lookup_policy", "compute_compensation"]`. Ghi vết handoff vào trace bằng `safe_dump()`.
5. **Thực thi điều tra chỉ đọc:** Chạy `run_readonly_investigators()` với `principal_id` của khách hàng. Nếu đơn hàng không hiển thị hoặc không thuộc sở hữu của khách hàng (`visible=False`), Orchestrator lập tức chuyển sang trạng thái `escalated`.
6. **Thu thập kết quả bồi hoàn:** Nhận kết quả tính toán từ investigator (`compute_compensation`). Nếu số tiền đề xuất $\le 0$, trả về `denied`.
7. **Yêu cầu hoàn phí qua Host:** Gửi toàn bộ mức bồi thường đề xuất (`proposal`) vào `durability.issue_refund(conn, claim_id, proposal, crash_at=crash_at)`. Host sẽ tự động trừ đi các khoản đã hoàn trước đó theo trần đơn hàng.
8. **Đảm bảo Crash Safety:** Bắt ngoại lệ `InjectedCrash`, ghi sự kiện crash vào trace và gọi `trace.write()` trước khi ném lại (`raise`) ngoại lệ để host kiểm tra.
9. **Đóng gói kết quả:** Gọi `finish()` để sinh đối tượng `RunResult` chuẩn hóa, tự động cập nhật ledger effects và số lượng audit `refund_committed`.

### 3.2. Các quyết định kỹ thuật quan trọng

- **Không dùng LLM để Redact dữ liệu:** Thay vì dùng LLM để tóm tắt hoặc làm sạch dữ liệu (vốn không được coi là sanitizer an toàn), tôi sử dụng cơ chế allowlist chặt chẽ của `make_handoff` để loại bỏ hoàn toàn `parent_secret` và thông tin cá nhân (PII) trước khi chuyển cho investigator.
- **Độc quyền thao tác ghi:** Investigator chỉ là công cụ thu thập thông tin. Mọi thao tác ghi nhận hoàn tiền phải do Orchestrator kích hoạt thông qua cổng Host `issue_refund`.
- **Truyền Full Quote thay vì Net Amount:** Để xử lý đúng trần hoàn tiền theo đơn hàng (Order Cap) ở các ca như T13, T14, Orchestrator truyền đúng mức quote đầy đủ; việc tính toán phần chênh lệch hay từ chối hoàn trùng hoàn toàn do Host đảm nhiệm.
- **Trace Contract v1:** Ghi nhận đầy đủ chuỗi sự kiện (`events`) trong lần chạy, khớp chính xác `run_id`, không ghi nhận các thông tin cấm (SĐT, địa chỉ, internal note, `CANARY_SECRET_*`).

### 3.3. Bổ sung kiểm thử Unit Test

Tạo file kiểm thử mới:

`src/tests/test_orchestrator_custom.py`

Bao gồm 2 test case kiểm tra chuyên sâu:

1. `test_orchestrator_handoff_safety_and_readonly`: Kiểm tra claim hợp lệ `C-001` được resolve chính xác 35.000 VND; đồng thời đọc nội dung trace JSON được tạo ra để khẳng định không tồn tại chuỗi cấm `CANARY_SECRET` hay `internal_note`.
2. `test_orchestrator_missing_order_id`: Kiểm tra claim `C-004` (thiếu `order_id`) được nhận diện và xử lý dừng sớm tại trạng thái `needs_info`, số tiền đề xuất bằng 0, không phát sinh giao dịch bồi hoàn.

### 3.4. Commit kỹ thuật chính

- Commit hash: `e0e5924`
- Commit message: `feat(orchestrator): add custom unit tests for handoff safety and error cases`
- Commit triển khai trước đó: `dd1287f` (`push shape orchestrator`)
- Các file thay đổi:
  - `src/lab8/shapes/orchestrator.py`
  - `src/tests/test_orchestrator_custom.py`

## 4. Bằng chứng

### 4.1. Đóng góp trên GitHub

Link commit kỹ thuật:

https://github.com/lam2121/K5-L3B-DAY08-NhomBaKhi-FromWorkflowsToAgents/commit/e0e5924

### 4.2. Chạy thử nghiệm thực tế trên claim mẫu

Kiểm tra với claim `C-001`, seed `11`:

- Run ID: `R-orchestrator-C-001-s11`
- Trạng thái: `resolved`
- Số tiền đề xuất: 35.000 VND
- Số tiền thực tế ghi nhận trên ledger: 35.000 VND
- Số audit `refund_committed`: 1
- Handoff: Được khử khuẩn (sanitized), chỉ cấp quyền `lookup_order`, `lookup_policy`, `compute_compensation`.
- Trace file: Được tạo mới, cấu trúc JSON hợp lệ, hoàn toàn sạch mã bí mật.

### 4.3. Kết quả kiểm thử

| Nội dung kiểm tra | Lệnh thực thi | Kết quả |
|---|---|---|
| Kiểm tra unit test cá nhân viết | `python -m pytest -q tests/test_orchestrator_custom.py` | **2 passed** |
| Kiểm tra toàn bộ 62 test của Shape C | `python -m pytest -q -m student -o addopts= -k orchestrator` | **62 passed** |
| Kiểm tra ma trận tổng thể toàn nhóm | `python -m pytest -q -m student -o addopts=` | **248 passed** |
| Tự kiểm tra trên bộ Hidden (`student_drop`) | `python -m lab8.benchmark --shapes ... --cases student_drop/...` | **200/200 trials Shape C hoàn thành (0 error, 0 leak, mean 2.90 steps)** |
| Cổng test Host | `python -m pytest -q` | **Passed (xanh)** |

## 5. Công cụ AI đã sử dụng

Tôi sử dụng các trợ lý AI (Gemini, ChatGPT) để hỗ trợ trong quá trình nghiên cứu tài liệu, thiết kế luồng điều phối và xây dựng bài kiểm thử.

Các mục đích cụ thể:
- Làm rõ sự khác biệt về mức độ tự chủ giữa Orchestrator (Shape C) và Workflow (Shape A), Swarm (Shape D).
- Hướng dẫn cấu trúc gọi `run_readonly_investigators` và thiết lập Handoff qua allowlist.
- Gợi ý xây dựng các unit test kiểm tra ranh giới bảo mật cho trace và handoff.
- Hỗ trợ giải thích các lỗi phát sinh trong quá trình chạy kiểm thử pytest trên môi trường Windows PowerShell.

### Cách tự kiểm chứng kết quả

Tôi luôn tuân thủ nguyên tắc không chấp nhận mù quáng output của AI:
- Đọc kỹ tài liệu nội bộ của bài lab: `docs/contracts.md`, `docs/business_rules.md`, `docs/architecture.md`.
- Trực tiếp chạy và kiểm tra kết quả bằng các lệnh test thực tế (`pytest`).
- Tự mở file trace JSON sinh ra sau khi chạy để rà soát thủ công các trường dữ liệu và đảm bảo không có rò rỉ thông tin nhạy cảm.

## 6. Tự đánh giá

Tôi đã hoàn thành tốt nhiệm vụ được giao là phát triển toàn diện Shape C (Orchestrator) và viết unit test kiểm chứng chuyên biệt cho phần việc của mình.

Qua bài lab này, tôi đã hiểu sâu sắc về:
- Cách thức vận hành mô hình Orchestrator - Subagent trong thực tế: Orchestrator đóng vai trò bộ não lập kế hoạch và tổng hợp, trong khi các worker/investigator bị giới hạn quyền truy cập chỉ đọc để đảm bảo an toàn tuyệt đối cho hệ thống.
- Tầm quan trọng của ranh giới an toàn dữ liệu: Dữ liệu trao đổi giữa các agent (Handoff) phải được lọc qua allowlist cứng thay vì phụ thuộc vào sự tự giác của mô hình ngôn ngữ.
- Tính toàn vẹn của giao dịch tài chính: Mọi giao dịch thay đổi trạng thái dữ liệu (ghi ledger) phải được cô lập và quản lý tập trung bởi Host với các cơ chế kiểm tra approval, trần hoàn tiền, và chống trùng lặp (idempotency).
