# Research card

File này nằm cố định ở `report/team/research_card.md`; `python -m lab8.check_submission` đọc cột "Nhóm điền" bằng máy.

Phần này nối tiếp phần mini research ở buổi lý thuyết (slide 62–63). Chọn **một** câu R1–R4, điền 6 dòng, rồi biến nó thành **một ablation** chạy được trong lab: giữ nguyên model (MockLLM), tool, seed, corpus và giá, chỉ thay đổi một biến.

| Câu | Nguồn (thư viện tham khảo, slide 68–69) | Câu hỏi gợi ý cho lab |
| --- | --- | --- |
| R1 · Scaling | Google Research 2026, *Towards a Science of Scaling Agent Systems* | Task claims chủ yếu tuần tự hay song song được? Dự đoán thêm investigator sẽ làm pass rate và cost/success thay đổi thế nào. |
| R2 · Failure taxonomy | MAST, NeurIPS 2025, *Why Do Multi-Agent LLM Systems Fail?* | Các trial fail của swarm (seed 55) thuộc nhóm nào: lỗi giao việc, lệch mục tiêu, hay lỗi kiểm chứng? |
| R3 · Architecture choices | AgentArch, AACL 2026 | Nếu đổi topology mà giữ nguyên mọi thứ khác, biến nào phải cố định để kết luận còn đúng? |
| R4 · Evaluation confounders | EMNLP 2026, *Rethinking Evaluation of MAS Efficiency* | Làm sao chứng minh chênh lệch giữa A/B/C/D là do topology, không phải do prompt, tool hay seed? |

## Phiếu của nhóm

Điền vào cột cuối. Không xóa hai cột đầu.

| Field | Hướng dẫn | Nhóm điền |
| --- | --- | --- |
| CÂU | R1 / R2 / R3 / R4 | R2 |
| SOURCE | Paper/blog, năm, URL, loại bằng chứng (benchmark, production report, blog kinh nghiệm) | MAST, NeurIPS 2025, arXiv:2503.xxxxx, Empirical Taxonomy & Multi-Agent Benchmark |
| CLAIM | Một kết luận gốc của nguồn. Không viết rộng hơn phạm vi paper | Hệ thống multi-agent dễ thất bại do lệch mục tiêu (misalignment) và thiếu cơ chế xác minh/kiểm chứng dữ liệu độc lập giữa các agent tham gia |
| BOUNDARY | Model / dataset / setup giới hạn kết luận đó | Đánh giá trên các tác vụ đa bước với kiến trúc cộng tác ngang hàng (peer-to-peer swarm) và trao đổi thông điệp tự do |
| HYPOTHESIS | Nếu đổi shape A→B (hoặc bật/tắt một thành phần), metric X sẽ đổi theo hướng nào, khoảng bao nhiêu | Khi chuyển từ Workflow (A) sang Swarm (D), độ ổn định sẽ giảm do agent dễ bị ảnh hưởng bởi dữ liệu người dùng; cụ thể ở seed 55, pass rate của Swarm sẽ giảm dưới 1.0 và phát sinh seed variance > 0 |
| METHOD | Biến giữ cố định: model, tools, seed, corpus, giá, evaluator. Biến duy nhất được thay đổi: … | Cố định: MockLLM, bộ tools, 14 claim public, bảng giá pricing.yaml, evaluator. Biến duy nhất thay đổi: Topology xử lý (Workflow tất định vs Swarm đa tác tử) |
| FAILURE / METRIC | Một lỗi dự kiến và cách đo nó: pass rate, pass^5, variance, cost/success, leak, bypass | Lỗi kiểm chứng do tin vào dữ liệu người dùng thay vì DB; đo bằng pass rate tại seed 55 (ca T02), pass^5 và seed variance trong benchmark |

## Kết quả ablation

- Lệnh đã chạy (copy nguyên văn): `python -m lab8.benchmark --shapes workflow,single,orchestrator,swarm --cases data/public_claims.jsonl --seeds 11,22,33,44,55 --out reports/benchmark.json`
- Run id / file report: `src/reports/benchmark.json`
- Kết quả so với hypothesis (đúng / sai / không kết luận được), kèm số liệu:
  * **Đúng hoàn toàn với giả thuyết.**
  * Workflow (Shape A) duy trì pass rate 1.0 (70/70) và seed variance bằng 0.0.
  * Ngược lại, Swarm (Shape D) bị giảm pass rate xuống 0.9857 (69/70 trial) và pass^5 giảm xuống 0.9286 (13/14 claim), làm xuất hiện seed variance là 0.000816. Nguyên nhân là ở seed 55, agent trong Swarm tin vào lời khai trong ticket của khách (trễ 5 ngày) thay vì số ngày thực tế trong database đơn hàng (2 ngày), dẫn đến hoàn tiền sai ở ca T02.
  * Chi phí trên mỗi lượt thành công của Swarm (49.57 VND) cao hơn 1.78 lần so với Workflow (27.86 VND).
- Giới hạn: MockLLM không phải model sản xuất, latency là `unavailable`.
