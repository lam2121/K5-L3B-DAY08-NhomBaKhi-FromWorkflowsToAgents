# Báo cáo cá nhân — Nguyễn Văn Lâm

## 1. Thông tin thành viên

- Họ tên: Nguyễn Văn Lâm
- MSSV: 2A202604115
- Email: nvl21122003@gmail.com
- GitHub: lam2121

## 2. Phần việc phụ trách

**Vai trò trong nhóm 4 người:** `ledger + evaluation` (Hệ thống Ledger, Durability, Benchmark & Đánh giá hiệu năng) kết hợp bổ sung kiểm thử cho **Shape B (Single Agent ReAct)**.

Trong bài lab này, tôi chịu trách nhiệm các mảng công việc trọng yếu sau:

1. **Kiểm soát tính bền vững và an toàn Ledger (Durability & Idempotency):**
   - Đảm bảo cơ chế idempotency của các shape thông qua khóa `refund:{claim_id}`, ngăn chặn hoàn tiền trùng lặp khi gọi lại (retry - T11).
   - Kiểm tra tính an toàn khi gặp sự cố crash trước hoặc sau điểm cam kết (checkpoint - T12), đảm bảo sau khi khôi phục chỉ ghi nhận đúng 1 dòng trong `refund_ledger` và 1 sự kiện audit `refund_committed`.
   - Chạy và xác thực bộ kiểm thử crash suite đạt tuyệt đối `20/20` tại `src/reports/crash.json`.

2. **Thực thi và Phân tích Benchmark (Evaluation CP5):**
   - Vận hành công cụ `lab8.benchmark` trên cả 4 kiến trúc (`workflow`, `single`, `orchestrator`, `swarm`) trên 14 claims public × 5 seeds ngẫu nhiên (`11, 22, 33, 44, 55`), tạo ra dữ liệu thực nghiệm gồm 280 trials tại `src/reports/benchmark.json`.
   - Phân tích các số đo quan trọng: Tỷ lệ thành công tổng thể (Pass rate), độ ổn định tuyệt đối qua 5 seed ($Pass^5$), độ phân kỳ do seed (Seed variance), và chi phí mô phỏng trên mỗi ca thành công (Cost per success).

3. **Bổ sung kiểm thử độc lập cho Shape B (Single Agent ReAct):**
   - Xây dựng bộ test riêng `src/tests/test_single.py` để kiểm thử toàn diện các nhánh rẽ của Single Agent: xử lý claim không tồn tại, claim thiếu thông tin đơn hàng, và luồng duyệt hoàn phí thành công thông qua Host.

---

## 3. Đóng góp cụ thể

### 3.1. Bổ sung bộ kiểm thử Unit Test cho Single Agent (`test_single.py`)

Tôi đã thiết kế và triển khai file kiểm thử độc lập tại:

`src/tests/test_single.py`

Bao gồm 3 ca kiểm thử chuyên sâu nhằm xác thực tính đúng đắn và an toàn của kiến trúc Single Agent:

1. **`test_single_unknown_claim_fails_safely` (Kiểm thử lỗi claim lạ):**
   - Đưa vào claim giả lập `C-UNKNOWN`.
   - Xác thực: Vòng lặp ReAct nhận diện claim không tồn tại ngay từ quan sát đầu tiên (`found: False`), trả về trạng thái `failed` với mã lỗi `unknown_claim`.
   - Đảm bảo tính toàn vẹn: Không gọi lệnh ghi vào SQLite, không tạo dòng ledger mới, không ghi audit commit.
   - Kiểm tra Trace Contract v1: File trace được sinh đúng chuẩn, `run_id` khớp, và tuyệt đối không rò rỉ canary secret.

2. **`test_single_missing_order_returns_needs_info` (Kiểm thử dừng sớm khi thiếu mã đơn):**
   - Sử dụng claim `C-004` (khách hàng không nhớ mã đơn hàng `order_id = null`).
   - Xác thực: Agent phát hiện thiếu `order_id` và dừng sớm ở trạng thái `needs_info` với lý do `missing_order_id`, mức đề xuất bằng 0.
   - Đảm bảo hệ thống không tiếp tục gọi model vô ích hay gọi công cụ ghi tiền.

3. **`test_single_successful_refund_execution` (Kiểm thử chu trình ReAct hoàn chỉnh):**
   - Chạy với claim hợp lệ `C-001` (đơn O-107 giao trễ 4 ngày).
   - Xác thực: ReAct duyệt tuần tự qua các công cụ đọc (`get_claim_view` $\rightarrow$ `lookup_order` $\rightarrow$ `lookup_policy` $\rightarrow$ `compute_compensation` $\rightarrow$ `lookup_refund_history`), sau đó chuyển số tiền đề xuất (35.000 VND) sang Host duyệt.
   - Host kiểm tra hợp lệ, ghi đúng 1 dòng vào `refund_ledger` và 1 audit `refund_committed`. Trace sạch không chứa `CANARY_SECRET_*`.

### 3.2. Thực thi và phân tích dữ liệu Benchmark (`benchmark.json`)

Tôi đã chạy toàn bộ ma trận kiểm thử thực nghiệm:
```bash
python -m lab8.benchmark --shapes workflow,single,orchestrator,swarm --cases data/public_claims.jsonl --seeds 11,22,33,44,55 --out reports/benchmark.json
```

Kết quả tạo ra file `src/reports/benchmark.json` (3.795 dòng, 280 trials) với các phát hiện định lượng quan trọng:
- **Tính ổn định của Deterministic Workflow:** Đạt pass rate 100% trên cả 5 seed ($Pass^5 = 1.0$), variance bằng 0, chi phí mô phỏng thấp nhất vì không lãng phí token vào việc suy luận tool selection.
- **Hiện tượng Seed Variance ở Swarm:** Swarm đạt pass rate cao nhưng bị gãy ở seed 55 trên claim `C-002`. Nguyên nhân do sự biến động trong lời giải của LLM khiến các tác tử phân rã không đạt được sự đồng thuận (Consensus Failure).
- **Chi phí của Single Agent ReAct:** Tiêu tốn số bước (`steps`) và số lần gọi model trung bình cao gấp nhiều lần so với Workflow, do phải duy trì ngữ cảnh hội thoại và gọi lặp ReAct loop.

### 3.3. Xác thực an toàn Crash & Idempotency

- Vận hành công cụ `lab8.crash_test` với 20 điểm tiêm lỗi ngẫu nhiên:
```bash
python -m lab8.crash_test --count 20 --out reports/crash.json
```
- Kết quả đạt tuyệt đối **`crash_safety: 20/20`**, chứng minh tính bền vững: việc tiêm ngoại lệ `InjectedCrash` trước hay sau khi ghi ledger không bao giờ gây ra hiện tượng hoàn tiền hai lần (Double Refund).

### 3.4. Commit kỹ thuật chính

- **Commit hash:** `54c098b`
- **Commit message:** `feat: add benchmark report and single test implementation`
- **Các file thay đổi / tạo mới:**
  - `src/tests/test_single.py` (+91 dòng)
  - `src/reports/benchmark.json` (+3.795 dòng)

---

## 4. Bằng chứng

### 4.1. Link commit kỹ thuật trên GitHub

- Commit hash: `54c098b`
- Link: `https://github.com/lam2121/K5-L3B-DAY08-NhomBaKhi-FromWorkflowsToAgents/commit/54c098b`

### 4.2. Dẫn chứng thực nghiệm cụ thể (Run ID)

1. **Run ID kiểm thử ReAct thành công:**
   - Run ID: `R-single-C-001-s11`
   - Shape: `single`, Claim ID: `C-001`, Seed: `11`
   - Trạng thái: `resolved`, Proposal Amount: 35.000 VND, Refund VND: 35.000 VND
   - Audit Commit: 1, Secret Leak: 0

2. **Dẫn chứng Crash Test:**
   - File bằng chứng: `src/reports/crash.json`
   - Kết quả: `"crash_safety": "20/20"`

### 4.3. Kết quả chạy kiểm thử tự động

| Nội dung kiểm tra | Lệnh thực thi | Kết quả |
|---|---|---|
| Kiểm tra test cá nhân viết | `python -m pytest -v tests/test_single.py` | **3 passed** in 0.67s |
| Cổng kiểm thử Host | `python -m pytest -q` (trong `src/`) | **60 passed** (xanh 100%) |
| Kiểm tra ma trận học viên | `python -m pytest -q -m student -o addopts=` | **248 passed** |
| Kiểm tra bài nộp | `python -m lab8.check_submission` | Shapes và Reports đều đạt `[ OK ]` |

---

## 5. Công cụ AI đã dùng

1. **Công cụ sử dụng:** Trợ lý AI (Google Antigravity / Gemini / Claude).
2. **Mục đích sử dụng:**
   - Hỗ trợ xây dựng cấu trúc kiểm thử unit test cho `test_single.py` tuân thủ đúng tiêu chuẩn pytest và fixture `public_db`.
   - Hỗ trợ trích xuất, phân tích cú pháp dữ liệu JSON từ file benchmark để tính toán các đại lượng thống kê ($Pass^5$, seed min-max).
3. **Cách tự kiểm tra kết quả (Verification):**
   - Tự tay chạy trực tiếp các lệnh kiểm thử qua terminal PowerShell.
   - Dùng script Python độc lập truy vấn trực tiếp cơ sở dữ liệu SQLite (`db.py`) để kiểm chứng số lượng dòng ledger và audit log `refund_committed` thực tế.
   - Kiểm tra hàm `check_trace()` để đảm bảo file trace v1 được sinh mới, không bị stale và không chứa bất kỳ chuỗi nhạy cảm nào thuộc họ `CANARY_SECRET_*`.

---

## 6. Tự đánh giá

- **Mức độ hoàn thành công việc:** 100%.
- **Chất lượng đóng góp:**
  - Đảm bảo toàn bộ tiêu chí về Durability và Crash Safety đạt điểm tối đa (20/20).
  - Cung cấp bộ dữ liệu thực nghiệm benchmark 280 trials hoàn chỉnh cho báo cáo ADR của nhóm.
  - Viết bộ kiểm thử chất lượng cao, độc lập, bảo vệ ranh giới an toàn cho Shape B (Single Agent).
