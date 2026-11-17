# Team

## Thông tin nhóm

- Tên nhóm: Nhóm Ba Khỉ
- Lớp: L3B
- Repo nhóm: `K5-L3B-DAY08-NhomBaKhi-FromWorkflowsToAgents` (xem [SUBMISSION.md](SUBMISSION.md))
- URL repo, nhánh nộp, commit chốt: https://github.com/lam2121/K5-L3B-DAY08-NhomBaKhi-FromWorkflowsToAgents, main

## Thành viên

| STT | Họ tên | MSSV | Email | GitHub | Vai trò |
| --: | ------ | ---- | ----- | ------ | ------- |
|   1 | Nguyễn Văn Lâm | 2A202604115 | 26ai.lamnv@vinuni.edu.vn | lam2121 | ledger + evaluation |
|   2 | Nguyễn Duy Hưng | 2A202604110 | 26ai.hungnd6@vinuni.edu.vn | Hungnd1208 | orchestrator + handoff |
|   3 | Đặng Nguyễn Nhật Minh | 2A202604118 | 26ai.minhdnn@vinuni.edu.vn | MN-HD | workflow + integration |
|   4 | Nguyễn Trung Dũng | 2A202604084 | bomgoa102@gmail.com | bomgoa1102 | single |

Gợi ý chia vai:

- Nhóm 6 người: integration; workflow; single agent; orchestrator; ledger/policy/crash; eval/report.
- Nhóm 4 người: workflow + integration; single; orchestrator + handoff; ledger + evaluation.

## Bảng đóng góp

`python -m lab8.check_submission` đọc bảng này bằng máy: giữ nguyên tiêu đề `## Bảng đóng góp` và các cột. Mỗi người một dòng: commit có nội dung và ít nhất một test đã thêm hoặc sửa.

| Người | Vai | Commit | Test đã thêm hoặc sửa |
| --- | --- | --- | --- |
| Nguyễn Văn Lâm | ledger + evaluation | 54c098b | test_single.py::test_single_successful_refund_execution |
| Nguyễn Duy Hưng | orchestrator + handoff | e0e5924 | test_orchestrator_custom.py::test_orchestrator_handoff_safety_and_readonly |
| Đặng Nguyễn Nhật Minh | workflow + integration | ffa17da | test_workflow.py::test_unknown_claim_fails_without_refund_and_writes_clean_trace |
| Nguyễn Trung Dũng | single | 2bd35df | test_single.py::test_single_unknown_claim_does_not_refund_and_writes_safe_trace |

## Cá nhân

Mỗi thành viên đồng thời tạo một báo cáo riêng trong `report/` theo dạng:

```text
report/team/MSSV_HoTen.md
```

Ví dụ: `report/team/20241234_NguyenVanAn.md`.

## 2A202604115_NguyenVanLam

### Phần việc phụ trách

- Phụ trách đo lường, đánh giá benchmark 4 kiến trúc trên 14 claims x 5 seeds (reports/benchmark.json).
- Phụ trách kiểm thử an toàn Ledger, Idempotency và Crash Safety 20/20 (reports/crash.json).
- Bổ sung bộ kiểm thử chuyên sâu cho Shape B (Single Agent) tại `src/tests/test_single.py`.
- Hoàn thiện ADR (decision_adr.md), Research Card (research_card.md) và tổng hợp Báo cáo nhóm (group_report.md).

### Đóng góp cụ thể

- Commit `54c098b`: `feat: add benchmark report and single test implementation`.
- Commit `14ffb60`: `docs: add team reports, individual contribution, research card, and decision ADR`.
- Viết 3 unit tests cho Single Agent (`test_single.py`), vận hành benchmark 280 trials và crash test 20/20.

### Bằng chứng

- Link commit: https://github.com/lam2121/K5-L3B-DAY08-NhomBaKhi-FromWorkflowsToAgents/commit/54c098b
- Link commit: https://github.com/lam2121/K5-L3B-DAY08-NhomBaKhi-FromWorkflowsToAgents/commit/14ffb60
- File báo cáo cá nhân: `report/team/2A202604115_NguyenVanLam.md`

## 2A202604110_NguyenDuyHung

### Phần việc phụ trách

- Triển khai Shape C (Orchestrator) tại `src/lab8/shapes/orchestrator.py`.
- Bảo đảm ranh giới handoff an toàn (sanitize) cho investigator chỉ đọc.

### Đóng góp cụ thể

- Commit `e0e5924`: `feat(orchestrator): add custom unit tests for handoff safety and error cases`.
- Viết test `test_orchestrator_custom.py`.

### Bằng chứng

- File: `report/team/2A202604110_NguyenDuyHung.md`

## 2A202604118_DangNguyenNhatMinh

### Phần việc phụ trách

- Triển khai Shape A (Deterministic Workflow) tại `src/lab8/shapes/workflow.py`.
- Tích hợp và chuẩn hóa luồng xử lý hoàn tiền tất định.

### Đóng góp cụ thể

- Commit `ffa17da`: `Implement deterministic Shape A workflow`.
- Viết test `test_workflow.py`.

### Bằng chứng

- File: `report/team/2A202604118_DangNguyenNhatMinh.md`

## 2A202604084_NguyenTrungDung

### Phần việc phụ trách

- Triển khai Shape B (Single Agent ReAct) trong `src/lab8/shapes/single.py`.
- Thiết lập chu trình quan sát, suy nghĩ và chọn công cụ đọc an toàn qua vòng lặp ReAct `worker=True`.

### Đóng góp cụ thể

- Commit `1202bf6`: `shape B` — triển khai `run_claim()`, hàm `decide()` giới hạn tối đa 8 bước; đọc claim, xác minh đơn hàng theo `principal_id`, đọc policy, tính bồi hoàn bằng code và chuyển quote đầy đủ cho Host `issue_refund`.
- Commit `2bd35df`: `add more test shape B` — bổ sung 2 ca kiểm thử trong `src/tests/test_single_custom.py`, sau đó được chuyển sang `src/tests/test_single.py`: kiểm tra claim lạ không tồn tại và kiểm tra xử lý hoàn tiền một phần khi gặp crash rồi khôi phục không bị hoàn trùng (exactly-once).

### Bằng chứng

- File báo cáo cá nhân: `report/team/2A202604084_NguyenTrungDung.md`
- Link commit chính: https://github.com/lam2121/K5-L3B-DAY08-NhomBaKhi-FromWorkflowsToAgents/commit/1202bf65c7bd793aa2f8291ad69eaf9d52c395fa
- Link commit test: https://github.com/lam2121/K5-L3B-DAY08-NhomBaKhi-FromWorkflowsToAgents/commit/2bd35dfd1927793879f462f6cb7fdf49e94f3a96
- Kết quả test: `tests/test_single.py` sau khi gộp đạt **5 passed** (gồm 2 test của Dũng và 3 test của Lâm); ma trận student Shape B đạt **62 passed**.
