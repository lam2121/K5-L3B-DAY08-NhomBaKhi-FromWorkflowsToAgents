# Báo cáo cá nhân — Nguyễn Văn Lâm

## 1. Thông tin thành viên

- Họ tên: Nguyễn Văn Lâm
- MSSV: 2A202604115
- Email: 26ai.lamnv@vinuni.edu.vn
- GitHub: lam2121
- Repository: `https://github.com/lam2121/K5-L3B-DAY08-NhomBaKhi-FromWorkflowsToAgents`

---

## 2. Phần việc phụ trách

**Vai trò chính (trong nhóm 4 người):** `ledger + evaluation` (Hệ thống Ledger, Durability, Benchmark & Đánh giá hiệu năng) kết hợp hoàn thiện **Kiểm thử độc lập cho Shape B (Single Agent ReAct)** và **Tổng hợp tài liệu kiến trúc (ADR, Research Card, Group Report)**.

Trong bài lab này, mình chịu trách nhiệm trực tiếp các mảng công việc:

1. **Vận hành Benchmark thực nghiệm và Đánh giá 4 Topology (CP5):**
   - Vận hành bộ công cụ đo kiểm chuẩn `lab8.benchmark` trên toàn bộ 4 kiến trúc: **Shape A (Deterministic Workflow)**, **Shape B (Single Agent ReAct)**, **Shape C (Orchestrator - Workers)**, và **Shape D (Swarm Reference)** qua 14 claims public × 5 seeds ngẫu nhiên (`11, 22, 33, 44, 55`), tạo ra ma trận dữ liệu 280 trials tại `src/reports/benchmark.json`.
   - Trích xuất và phân tích các chỉ số định lượng then chốt: Tỷ lệ thành công tổng thể (Pass rate), độ ổn định tuyệt đối qua 5 seed ($Pass^5$), độ biến thiên do hạt giống ngẫu nhiên (Seed variance), phân phối số bước thực thi (Mean / p95 steps) và chi phí mô phỏng trên mỗi lần giải quyết thành công (Cost per success - VND).

2. **Kiểm soát an toàn Ledger, Idempotency & Crash Safety (CP3, CP4):**
   - Đảm bảo cơ chế Idempotency dựa trên khóa `refund:{claim_id}`, ngăn chặn hoàn tiền trùng lặp khi retry (T11).
   - Kiểm thử an toàn lỗi sập (Crash Safety) qua 20 điểm tiêm ngoại lệ `InjectedCrash` bằng `lab8.crash_test`, đảm bảo tính bền vững: sau khi phục hồi chỉ tồn tại duy nhất 1 dòng trong `refund_ledger` và 1 sự kiện audit `refund_committed` (`reports/crash.json` đạt tuyệt đối `20/20`).

3. **Bổ sung bộ kiểm thử Unit Test cho Shape B (Single Agent ReAct):**
   - Thiết kế và triển khai file kiểm thử độc lập `src/tests/test_single.py` kiểm tra các nhánh rẽ an toàn của ReAct loop: claim không tồn tại (`C-UNKNOWN`), claim thiếu mã đơn hàng (`C-004`), và luồng hoàn phí thành công chuẩn mực (`C-001`).

4. **Xây dựng Bản ghi quyết định kiến trúc (ADR), Phiếu nghiên cứu & Báo cáo nhóm:**
   - Trực tiếp soạn thảo và hoàn thiện **Bản ghi quyết định kiến trúc (`report/team/decision_adr.md`)**: Lựa chọn Shape A (Workflow) theo nguyên lý "ít tự chủ nhất" (*principle of least autonomy*), bảo vệ quyết định bằng dữ liệu thực nghiệm, phân tích rủi ro của Multi-Agent và xác định rõ các điều kiện đảo ngược quyết định kiến trúc.
   - Hoàn thiện **Phiếu nghiên cứu khoa học (`report/team/research_card.md`)**: Phân tích đối chiếu 4 bài báo khoa học hàng đầu (NeurIPS 2024 SWE-bench, NeurIPS 2025 MAST, AACL 2026 AgentArch, EMNLP 2026 Evaluation of MAS Efficiency).
   - Chắp bút tổng hợp **Báo cáo nhóm (`report/team/group_report.md`)**: Kết nối các mảng công việc của 4 thành viên thành tài liệu khoa học thống nhất, mạch lạc.

---

## 3. Đóng góp cụ thể

### 3.1. Triển khai bộ kiểm thử Unit Test `test_single.py`

mình đã viết và đẩy lên kho lưu trữ file kiểm thử tại:

`src/tests/test_single.py`

Bao gồm 3 ca kiểm thử xác thực tính đúng đắn và ranh giới an toàn của Shape B (Single Agent ReAct):

1. **`test_single_unknown_claim_fails_safely` (Xử lý claim không tồn tại):**
   - Đầu vào: Claim giả lập `C-UNKNOWN`.
   - Xác thực: Vòng lặp ReAct phát hiện claim không tồn tại ngay từ quan sát đầu tiên (`found: False`), trả về `status: "failed"` với mã lỗi `unknown_claim`.
   - Tính toàn vẹn Ledger: Không gọi lệnh ghi, không tạo dòng `refund_ledger`, không sinh audit `refund_committed`.
   - Bảo mật Trace Contract v1: File trace được ghi nhận mới, `run_id` khớp chuẩn, và tuyệt đối không rò rỉ canary token (`assert "CANARY_SECRET_" not in str(trace)`).

2. **`test_single_missing_order_returns_needs_info` (Dừng sớm khi thiếu mã đơn):**
   - Đầu vào: Claim `C-004` (khách hàng không nhớ mã đơn hàng, `order_id = null`).
   - Xác thực: Agent phát hiện thiếu `order_id` và dừng sớm tại trạng thái `needs_info`, số tiền đề xuất bằng 0, không gọi model dư thừa hay gọi công cụ ghi tiền.

3. **`test_single_successful_refund_execution` (Chu trình ReAct hoàn chỉnh):**
   - Đầu vào: Claim hợp lệ `C-001` (đơn O-107 giao trễ 4 ngày).
   - Xác thực: Agent thực thi ReAct qua các bước đọc dữ kiện (`get_claim_view` $\rightarrow$ `lookup_order` $\rightarrow$ `lookup_policy` $\rightarrow$ `compute_compensation` $\rightarrow$ `lookup_refund_history`), sau đó đề xuất 35.000 VND sang Host duyệt.
   - Host xác thực hợp lệ, ghi đúng 1 dòng vào `refund_ledger` và 1 audit `refund_committed`. Trace sạch và đúng hợp đồng v1.

### 3.2. Vận hành thực nghiệm Benchmark (`benchmark.json`)

mình đã thực thi toàn bộ lệnh benchmark trên cả 4 kiến trúc:
```bash
python -m lab8.benchmark --shapes workflow,single,orchestrator,swarm --cases data/public_claims.jsonl --seeds 11,22,33,44,55 --out reports/benchmark.json
```

Kết quả tạo ra file `src/reports/benchmark.json` (3.795 dòng, 280 trials), cung cấp bức tranh đối chiếu toàn diện:

| Chỉ số | Shape A (Workflow) | Shape B (Single Agent) | Shape C (Orchestrator) | Shape D (Swarm Reference) |
|---|:---:|:---:|:---:|:---:|
| **Pass rate** | **100% (70/70)** | 100% (70/70) | 100% (70/70) | 98.57% (69/70) |
| **Pass^5** (ổn định qua 5 seed) | **1.0 (14/14)** | 1.0 (14/14) | 1.0 (14/14) | 0.9286 (13/14) |
| **Seed Variance** | **0.0** | 0.0 | 0.0 | 0.0008 |
| **Cost / success (mô phỏng, VND)** | **27.86** | 46.33 | 47.90 | 49.57 |
| **Mean / p95 steps** | **4.43 / 6.00** | 9.07 / 13.00 | 8.86 / 12.00 | 14.19 / 18.00 |
| **Model calls (Mean)** | **0.0** | 4.07 | 1.00 | 4.29 |
| **Tool calls (Mean)** | **3.43** | 4.00 | 6.86 | 8.90 |

### 3.3. Soạn thảo Bản ghi quyết định kiến trúc (`decision_adr.md`)

Dựa trên dữ liệu thực nghiệm, mình đã hoàn thiện `report/team/decision_adr.md` với các nội dung trọng tâm:
- **Lựa chọn chính thức:** Chọn **Shape A (Workflow)** với Pass Rate 1.0, Pass^5 1.0, Cost 27.86 VND/success, Seed Variance 0.0, Crash Safety 20/20, Secret Leak = 0.
- **Lập luận bác bỏ Multi-Agent trong bài toán này:** Multi-agent (Swarm) tốn chi phí token gấp 1.78x, số bước gấp 3.2x và gây ra lỗi đồng thuận (Consensus Failure) làm fail claim `C-002` ở seed 55.
- **Điều kiện đảo chiều quyết định (Falsifiability):** Xác định 3 điều kiện doanh nghiệp thực tế để chuyển sang Agent: (1) Dữ liệu phi cấu trúc phức tạp cần đa phương thức (hình ảnh thiệt hại kiện hàng); (2) Quy định nghiệp vụ biến động động theo thời gian thực; (3) Quy trình điều tra bất đồng bộ đa phòng ban (pháp lý, kho, bảo hiểm).
- **Ranh giới bảo mật Trace:** Mô tả cơ chế allowlist ngăn chặn rò rỉ `CANARY_SECRET_*`, PII khách hàng, và phương thức chứng minh an toàn của đội ngũ bảo mật.

### 3.4. Hoàn thiện Phiếu nghiên cứu khoa học (`research_card.md`)

mình đã trả lời và đối chiếu cả 4 chủ đề nghiên cứu:
- **R1 (SWE-bench / Baseline bias):** Chứng minh rủi ro so sánh không công bằng nếu các shape dùng prompt/công cụ khác nhau; giải pháp của lab là cố định MockLLM, bộ công cụ bọc và pricing chung.
- **R2 (MAST / Failure taxonomy):** Phân loại lỗi của Swarm ở seed 55 vào nhóm *Lệch mục tiêu & Lỗi kiểm chứng (Goal Drift & Verification Failure)* khi tin vào ticket của người dùng thay vì đối chiếu database.
- **R3 (AgentArch / Architecture choices):** Xác định biến độc lập duy nhất là cấu trúc liên lạc (Topology) giữa các agent; cố định dữ liệu thế giới, công cụ và quy định nghiệp vụ.
- **R4 (Evaluation confounders):** Chứng minh chênh lệch hiệu năng hoàn toàn bắt nguồn từ topology thông qua thực nghiệm đối chứng đa hạt giống (Multi-seed evaluation: 11, 22, 33, 44, 55).

### 3.5. Chắp bút tổng hợp Báo cáo nhóm (`group_report.md`)

- Tổ chức báo cáo nhóm với 7 phần chuẩn mực theo yêu cầu học thuật.
- Trình bày trực quan bảng đối sánh 4 kiến trúc và phân tích chuyên sâu về Durability, Idempotency và Trace Contract v1.

### 3.6. Lịch sử commit kỹ thuật đã đẩy lên Git (Pushed Commits)

Toàn bộ đóng góp của mình được thể hiện qua các commit do chính tài khoản của mình đẩy lên nhánh `main`:

1. **Commit `54c098b`:**
   - Hash: `54c098b21633df0daaa104a1dcf92e223177a71e`
   - Message: `feat: add benchmark report and single test implementation`
   - Files: `src/tests/test_single.py` (+91 dòng), `src/reports/benchmark.json` (+3.795 dòng).
2. **Commit `14ffb60`:**
   - Hash: `14ffb60b43815e24c700bf40c62cc2462ec2a617`
   - Message: `docs: add team reports, individual contribution, research card, and decision ADR`
   - Files: `report/team/decision_adr.md` (+46 dòng), `report/team/research_card.md` (+24 dòng), `report/team/group_report.md` (+125 dòng), `report/team/2A202604115_NguyenVanLam.md` (+135 dòng).

---

## 4. Bằng chứng

### 4.1. Link commit trên GitHub

- Commit `54c098b`: `https://github.com/lam2121/K5-L3B-DAY08-NhomBaKhi-FromWorkflowsToAgents/commit/54c098b`
- Commit `14ffb60`: `https://github.com/lam2121/K5-L3B-DAY08-NhomBaKhi-FromWorkflowsToAgents/commit/14ffb60`

### 4.2. Dẫn chứng thực nghiệm cụ thể (Run ID)

- **Run ID kiểm thử ReAct thành công:** `R-single-C-001-s11` (Shape `single`, Claim `C-001`, Seed `11`, Status `resolved`, Proposal 35.000 VND, Refund 35.000 VND, Audit Commit 1).
- **Run ID đại diện cho Shape chọn (Workflow):** `R-workflow-C-001-s11` (Status `resolved`, Cost 20 VND, Audit Commit 1).
- **Crash Test:** `src/reports/crash.json` đạt tuyệt đối `crash_safety: "20/20"`.

### 4.3. Kết quả chạy kiểm thử tự động

| Nội dung kiểm tra | Lệnh thực thi | Kết quả |
|---|---|---|
| Unit test cá nhân viết | `python -m pytest -v tests/test_single.py` | **3 passed** in 0.67s |
| Cổng kiểm thử Host | `python -m pytest -q` (chạy trong `src/`) | **60 passed** (xanh 100%) |
| Kiểm tra ma trận học viên | `python -m pytest -q -m student -o addopts=` | **248 passed** |
| Định dạng bài nộp | `python -m lab8.check_submission` | **0 FAIL** (Shapes, Reports, Docs đạt chuẩn) |

---

## 5. Công cụ AI đã dùng

1. **Công cụ sử dụng:** Trợ lý AI (Google Antigravity / Gemini / Claude).
2. **Mục đích sử dụng:**
   - Hỗ trợ xây dựng cấu trúc kiểm thử unit test cho `test_single.py` chuẩn pytest fixture.
   - Hỗ trợ tính toán thống kê, trích xuất dữ liệu đa chiều từ file `benchmark.json` (3.795 dòng).
   - Hỗ trợ tra cứu tài liệu học thuật và chuẩn hóa thuật ngữ khoa học trong ADR và Research Card.
3. **Cách tự kiểm tra kết quả (Verification):**
   - Trực tiếp chạy và kiểm tra đầu ra terminal qua các lệnh pytest và script kiểm tra của ban tổ chức.
   - Truy vấn SQLite độc lập bằng hàm `db.connect()` để kiểm tra độ tin cậy của ledger và số lượng bản ghi audit `refund_committed`.
   - Xác thực Trace Contract v1 qua hàm `lab8.metrics.check_trace()`, quét chuỗi cấm `CANARY_SECRET_*` trong toàn bộ file kết quả.

---

## 6. Tự đánh giá

- **Mức độ hoàn thành công việc:** 100%.
- **Chất lượng đóng góp:**
  - Hoàn thành trọn vẹn cả phần kỹ thuật (Test single agent, Benchmark, Crash safety) và phần tài liệu học thuật then chốt (ADR, Research card, Group report).
  - Đóng góp trực tiếp vào 2 commit kỹ thuật và tài liệu lớn của nhóm (`54c098b` và `14ffb60`), đảm bảo nhóm vượt qua toàn bộ tiêu chí Rubric và 3 điều kiện must-pass.
