# Decision record

Điền sau dấu `:` trên cùng dòng, không xóa nhãn. Giảng viên và `python -m lab8.check_submission` (chạy trong `src/`) đọc các dòng này bằng máy. Không đổi tên hay dời file này khỏi `report/team/`.
`Shape chọn` phải là đúng một trong: `workflow`, `single`, `orchestrator`, `swarm`. Đây là shape được chấm cổng hidden.

- Shape chọn: workflow
- Commit hash: 9762582
- Run id dẫn chứng: R-workflow-C-001-s11
- Pass rate / pass^5 / seed min-max / variance: 1.0 / 1.0 / 1.0 - 1.0 / 0.0
- Cost per success (mô phỏng, VND): 27.86
- Crash safety: 20/20 (src/reports/crash.json)
- Secret leak / approval bypass: 0 / 0

## Vì sao shape này

Nhóm quyết định chọn Shape A (**Workflow**) làm kiến trúc chính thức để nộp bài và chấm cổng hidden dựa trên nguyên lý cốt lõi của bài lab: **"chọn kiến trúc ít tự chủ nhất mà vẫn hoàn thành tốt công việc"** (*principle of least autonomy*).
Khi so sánh trên cùng corpus 14 claim public qua 5 seed (11, 22, 33, 44, 55):
- Shape A đạt **Pass Rate tuyệt đối 100% (70/70 trial)** và **Pass^5 đạt 1.0** (14/14 claim pass cả 5 seed).
- Độ biến thiên giữa các seed (**Seed Variance**) bằng **0.0**, tính tất định hoàn hảo, không bị ảnh hưởng bởi tính ngẫu nhiên của mô hình hay các cú sốc seed.
- Chi phí giả lập thấp nhất trong 4 kiến trúc: chỉ **27.86 VND / success** (so với Single Agent: 46.33 VND, Orchestrator: 47.90 VND, Swarm: 49.57 VND).
- Số bước thực thi gọn gàng (mean 4.43 bước), không tốn chi phí gọi model không cần thiết.

## Có đáng đổi lấy multi-agent không

**Hoàn toàn không đáng đổi trong bối cảnh bài toán xử lý claim vận chuyển hiện tại.**
Thực nghiệm benchmark cho thấy việc tăng tính tự chủ từ Workflow lên Single Agent hay Multi-Agent (Orchestrator, Swarm) làm tăng chi phí token từ 1.66x đến 1.78x và tiềm ẩn rủi ro sai lệch:
- Swarm tham chiếu bị rớt pass rate xuống 98.57% (pass^5 chỉ đạt 92.86%) và phát sinh seed variance 0.0008 do ở seed 55 swarm tin vào lời khai trong ticket của khách thay vì kiểm chứng database đơn hàng (T02).
- Cả Orchestrator và Single Agent dù đạt pass rate 100% trên tập public nhưng tiêu tốn thêm nhiều model calls và tool calls mà không đem lại giá trị gia tăng nào so với workflow tất định.

**Điều kiện làm quyết định đảo lại:**
Quyết định kiến trúc sẽ đảo ngược sang Single Agent hoặc Orchestrator khi:
1. Dữ liệu đầu vào mang tính phi cấu trúc cao (ví dụ: ticket chứa hình ảnh thiệt hại thực tế cần suy luận thị giác, nhiều tài liệu thỏa thuận tùy biến giữa đối tác doanh nghiệp).
2. Quy định nghiệp vụ thay đổi động liên tục theo thời gian thực (real-time dynamic policy) mà code tĩnh không thể cập nhật kịp thời bằng logic `if/else`.
3. Bài toán mở rộng sang điều tra liên chuỗi cần phân rã nhiều tác vụ chuyên biệt không đồng bộ (pháp lý, bảo hiểm bên thứ ba, kho bãi).

## Trace và bằng chứng

Trace của nhóm tuân thủ nghiêm ngặt **Trace Contract v1**:
- Ghi nhận các event hợp lệ: `claim_lookup`, `order_view`, `quote`, `decision`, `crash`.
- **Các trường cố ý KHÔNG ghi vào trace:** `CANARY_SECRET_*`, raw header, số điện thoại, địa chỉ giao hàng, tên mặt hàng, ghi chú nội bộ (`internal_note`). Các trường này bị chặn bởi cơ chế allowlist của các hàm tool bọc an toàn (`get_claim_view`, `lookup_order`).
- **Cách đội bảo mật chứng minh hệ thống không lộ secret:** Nếu trace nằm ngoài vùng quét tự động, đội bảo mật kiểm chứng bằng cách:
  1. Sử dụng công cụ quét tĩnh (static scanner) quét toàn bộ log file với regex tìm kiếm các chuỗi khóa bí mật và mẫu PII.
  2. Kiểm tra mã nguồn để xác thực không có câu lệnh in log hay đẩy raw row DB ra stdout/file.
  3. Dựa trên kết quả tự động của crash test và hidden grade (`secret_leak_count = 0`).

## Giới hạn

- MockLLM trong bài lab là mô hình mô phỏng theo seed, không phản ánh toàn bộ sự bất định (non-determinism), ảo giác (hallucination) hay độ trễ mạng thực tế của LLM thương mại trong môi trường production.
- Độ trễ của MockLLM được quy định là `unavailable`, do đó chỉ số đánh giá tập trung vào số bước (steps), chi phí token giả lập và độ chính xác logic.
- Không chỉnh sửa file JSON kết quả để đáp ứng ngưỡng tiêu chí; toàn bộ số liệu đều được ghi nhận trực tiếp từ quá trình thực thi lệnh benchmark chính thức.
