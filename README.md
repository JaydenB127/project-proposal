# Project Proposal

> ⚠️ **Lưu ý quan trọng:** Proposal sau khi được thầy xác nhận sẽ làm cơ sở để chấm điểm cuối kỳ. Hãy đọc kỹ và chỉnh sửa nội dung trước khi nộp.

---

## THÔNG TIN

### Nhóm

- Thành viên 1: `<họ tên>` - `<msv>`
- Thành viên 2: `<họ tên>` - `<msv>`
- Thành viên 3: `<họ tên>` - `<msv>`
- Thành viên 4: `<họ tên>` - `<msv>`

### Git

Git repository: `<link>`

```
Lưu ý:
- Chỉ tạo git repository một lần, nếu đổi link repo nhóm sẽ bị trừ điểm.
```

---

## MÔ TẢ DỰ ÁN

### Ý tưởng

**Experiment Tracking System** là một ứng dụng web giúp các kỹ sư và nhà nghiên cứu ML/AI theo dõi, quản lý và so sánh các thí nghiệm machine learning một cách có hệ thống thông qua giao diện trực quan.

**Lý do chọn đề tài:**  
Trong quá trình huấn luyện mô hình ML, người dùng thường chạy hàng chục đến hàng trăm thí nghiệm với các tham số (hyperparameters) khác nhau. Việc ghi chép thủ công bằng file Excel hoặc ghi chú rời rạc rất dễ mất dữ liệu, khó tái hiện kết quả và khó so sánh giữa các lần chạy.

**Điểm khác biệt so với các phần mềm hiện tại (MLflow, Weights & Biases):**
- Giao diện thân thiện, đơn giản, phù hợp cho sinh viên và người mới bắt đầu
- Không yêu cầu cấu hình phức tạp, chạy được trên máy cá nhân (localhost)
- Dashboard trực quan với biểu đồ so sánh nhiều experiment cùng lúc
- Tích hợp tính năng cộng tác nhóm: phân quyền thành viên, chia sẻ kết quả

### Chi tiết

Hệ thống phục vụ 2 nhóm người dùng chính:

**1. Researcher / ML Engineer:**
- Tạo và đặt tên **Experiment** (đại diện cho một dự án / bài toán nghiên cứu)
- Mỗi Experiment chứa nhiều **Run** (mỗi lần chạy thử với bộ tham số khác nhau)
- Mỗi Run lưu lại:
  - **Hyperparameters:** learning_rate, epochs, batch_size, optimizer, ...
  - **Metrics:** accuracy, loss, F1-score, AUC, ... (theo từng epoch/step)
  - **Artifacts:** file model (.pkl, .h5), biểu đồ loss curve, confusion matrix, ...
  - **Metadata:** thời gian bắt đầu/kết thúc, trạng thái (running / success / failed)
- Xem dashboard với biểu đồ trực quan
