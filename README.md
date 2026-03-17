# Project Proposal

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

**Experiment Tracking System** là một hệ thống web giúp các kỹ sư và nhà nghiên cứu ML/AI theo dõi, quản lý và so sánh các thí nghiệm machine learning một cách có hệ thống.

**Lý do chọn đề tài:**  
Trong quá trình huấn luyện mô hình ML, người dùng thường chạy hàng chục đến hàng trăm thí nghiệm với các tham số (hyperparameters) khác nhau. Việc ghi chép thủ công bằng file Excel hoặc ghi chú rời rạc rất dễ mất dữ liệu, khó tái hiện kết quả và khó so sánh giữa các lần chạy.

**Điểm khác biệt so với các phần mềm hiện tại (MLflow, Weights & Biases):**
- Giao diện thân thiện, đơn giản, phù hợp cho sinh viên và người mới bắt đầu
- Không yêu cầu cấu hình phức tạp, triển khai được trên máy cá nhân (localhost)
- Hỗ trợ dashboard trực quan để so sánh nhiều experiment cùng lúc
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
- Xem lại lịch sử các Run, lọc và so sánh kết quả qua biểu đồ trực quan

**2. Team Admin / Project Manager:**
- Quản lý danh sách Experiment của nhóm
- Mời thành viên, phân quyền (Viewer / Editor / Admin)
- Export báo cáo kết quả dạng CSV

---

## PHÂN TÍCH & THIẾT KẾ

### 1. Actors (Tác nhân)

| Actor | Mô tả |
|-------|-------|
| Unauthenticated User | Người dùng chưa đăng nhập, chỉ có thể đăng ký / đăng nhập |
| Researcher | Người dùng đã đăng nhập, tạo và quản lý experiment / run |
| Team Admin | Quản lý thành viên nhóm, phân quyền, xem toàn bộ dự án |
| System | Tự động lưu log, cập nhật trạng thái run |

### 2. Danh sách Use Cases

| STT | Use Case | Actor |
|-----|----------|-------|
| UC01 | Đăng ký tài khoản | Unauthenticated User |
| UC02 | Đăng nhập / Đăng xuất | All |
| UC03 | Tạo / Sửa / Xóa Experiment | Researcher |
| UC04 | Tạo Run mới, log params & metrics | Researcher |
| UC05 | Xem danh sách Run theo Experiment | Researcher |
| UC06 | So sánh các Run qua biểu đồ | Researcher |
| UC07 | Upload / Xem Artifact của Run | Researcher |
| UC08 | Quản lý thành viên nhóm | Team Admin |
| UC09 | Phân quyền Viewer / Editor / Admin | Team Admin |
| UC10 | Export kết quả ra CSV | Researcher, Team Admin |

### 3. Thiết kế Cơ sở dữ liệu

**Các bảng chính:**

| Bảng | Các cột chính |
|------|---------------|
| `users` | id, name, email, password_hash, created_at |
| `experiments` | id, name, description, owner_id, created_at |
| `experiment_members` | experiment_id, user_id, role (viewer/editor/admin) |
| `runs` | id, experiment_id, name, status, started_at, ended_at |
| `params` | id, run_id, key, value |
| `metrics` | id, run_id, key, value, step, timestamp |
| `artifacts` | id, run_id, file_name, file_path, file_type, created_at |

### 4. Kiến trúc hệ thống

```
┌─────────────────────────────────────────────────────────┐
│                        Client                           │
│            React + Chart.js + Tailwind CSS              │
└────────────────────────┬────────────────────────────────┘
                         │ REST API (HTTP/JSON)
┌────────────────────────▼────────────────────────────────┐
│                  Backend (FastAPI)                      │
│     Authentication │ Experiment API │ Run API          │
└──────────┬──────────────────────────────────┬───────────┘
           │                                  │
┌──────────▼──────────┐           ┌───────────▼───────────┐
│    PostgreSQL        │           │   File Storage        │
│  (Metadata & Logs)  │           │  (Artifacts / Models) │
└─────────────────────┘           └───────────────────────┘
```

**Stack công nghệ:**

| Thành phần | Công nghệ |
|------------|-----------|
| Frontend | React, Chart.js, Tailwind CSS |
| Backend | Python, FastAPI |
| Database | PostgreSQL |
| Authentication | JWT (JSON Web Token) |
| File Storage | Local filesystem (MVP), MinIO (phase sau) |
| ORM | SQLAlchemy |

---

## KẾ HOẠCH

### MVP (Thời hạn hoàn thành: 12.04.2026)

**Các chức năng MVP:**
1. Đăng ký / Đăng nhập bằng email + mật khẩu (JWT)
2. Tạo, sửa, xóa Experiment
3. Tạo Run mới và log hyperparameters + metrics
4. Xem danh sách Run, lọc theo Experiment
5. Biểu đồ so sánh metrics (line chart) giữa các Run
6. Phân quyền cơ bản: Viewer / Editor

**Kế hoạch kiểm thử MVP:**
- Unit test các API endpoint với `pytest`
- Test thủ công các luồng chính:
  - Luồng 1: Đăng ký → Đăng nhập → Tạo experiment → Log run → Xem dashboard
  - Luồng 2: Phân quyền: user không được xem / sửa experiment của người khác
  - Luồng 3: So sánh kết quả 2 Run trong cùng 1 Experiment
- Kiểm tra xử lý lỗi: input không hợp lệ, token hết hạn, run không tồn tại

**Chức năng dự kiến ở phase tiếp theo (Beta):**
- Upload và quản lý Artifact (file model, hình ảnh biểu đồ)
- Tính năng mời thành viên vào nhóm qua email
- Export báo cáo kết quả dạng CSV
- Giao diện so sánh nâng cao: scatter plot, parallel coordinates

### Beta Version (Thời hạn dự kiến: 10.05.2026)

- **Kết quả kiểm thử:** *(điền sau khi hoàn thành kiểm thử)*
- **Báo cáo:** *(điền sau)*
- **Thời hạn hoàn thành dự kiến:** 05.05.2026

---

## CÂU HỎI

- Artifact (file model) trong MVP có cần hỗ trợ upload thực sự hay chỉ cần lưu đường dẫn tham chiếu?
- Hệ thống có cần hỗ trợ real-time log (streaming metrics theo từng epoch) trong MVP không?
- Tiêu chí chấm điểm cho phần so sánh experiment được đánh giá như thế nào?
- Có yêu cầu deploy lên server thực tế (production) hay chỉ cần chạy được trên localhost?

---
