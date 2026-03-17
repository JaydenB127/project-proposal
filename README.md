<div align="center">

#  Experiment Tracking System

**Ứng dụng web theo dõi, quản lý và so sánh các thí nghiệm Machine Learning/ Deep Learning một cách trực quan**


</div>

## Nhóm phát triển

| Thành viên | MSSV | Vai trò |
|------------|------|---------|
| Bùi Thành Đạt | 23724811  | Trường nhóm  |
| La Thiên Bảo | 23723801 | Thành viên |
| Lê Ngọc Huy | 23727381 | Thành viên |
| Bùi Huy Bảo | 23720161 | 	Thành viên |

---

---

##  Tổng quan dự án

**Experiment Tracking System là một ứng dụng web cho phép người dùng tạo, lưu trữ và so sánh các thí nghiệm machine learning một cách có hệ thống. Thay vì ghi chép kết quả bằng Excel hay ghi chú rời rạc, người dùng có thể log hyperparameters và metrics của từng lần chạy, rồi xem lại qua dashboard với biểu đồ trực quan.
Lý do chọn đề tài: Trong quá trình học các môn Machine Learning, nhóm nhận thấy khi thử nghiệm nhiều bộ tham số khác nhau (learning rate, batch size, số epochs...), việc nhớ lại "lần chạy nào cho kết quả tốt nhất" rất khó nếu không ghi chép cẩn thận. Excel thì lộn xộn, ghi chú tay thì dễ mất — đây là vấn đề thực tế nhóm đã gặp.
Điểm khác so với phần mềm hiện có:
Các công cụ chuyên nghiệp như MLflow hay Weights & Biases rất mạnh nhưng đòi hỏi cấu hình phức tạp, cần hiểu về Docker, server, và thường tích hợp trực tiếp vào code Python. Dự án này hướng đến đối tượng là sinh viên hoặc người mới học ML với cách tiếp cận đơn giản hơn: người dùng tự nhập kết quả qua giao diện web, không cần cài đặt thêm bất cứ thứ gì, chạy được ngay trên localhost.

> Người dùng chỉ cần đăng nhập, tạo experiment, log kết quả từng run, và ngay lập tức thấy được biểu đồ so sánh trực quan giữa các lần thử nghiệm.

So sánh với các công cụ hiện tại như **MLflow** hay **Weights & Biases**, chúng tôi tập trung vào:

1. **Giao diện đơn giản, không cần cấu hình phức tạp** — chạy được ngay trên máy cá nhân (localhost)
2. **Dashboard trực quan** — biểu đồ line chart, bar chart so sánh metrics giữa các run
3. **Cộng tác nhóm** — phân quyền Viewer / Editor / Admin, chia sẻ kết quả trong team
4. **Phù hợp sinh viên** — không yêu cầu kiến thức hạ tầng cloud hay DevOps

---

##  Demo giao diện

> *(Cập nhật ảnh chụp màn hình sau khi hoàn thành MVP)*

| Dashboard | So sánh Runs | Quản lý Experiment |
|:---------:|:------------:|:-----------------:|
| ![dashboard](docs/images/dashboard.png) | ![compare](docs/images/compare.png) | ![experiments](docs/images/experiments.png) |

---

##  Kiến trúc hệ thống

```
┌─────────────────────────────────────────────────────────┐
│                     Người dùng                          │
└────────────────────────┬────────────────────────────────┘
                         │ HTTP / HTTPS
┌────────────────────────▼────────────────────────────────┐
│              Frontend — React + Tailwind CSS            │
│   Dashboard │ Charts (Recharts) │ Table (TanStack)      │
└────────────────────────┬────────────────────────────────┘
                         │ REST API (JSON)
┌────────────────────────▼────────────────────────────────┐
│               Backend — Python FastAPI                  │
│   Auth (JWT) │ Experiment API │ Run API │ Metric API    │
└──────────┬──────────────────────────────────┬───────────┘
           │                                  │
┌──────────▼──────────┐           ┌───────────▼───────────┐
│     PostgreSQL       │           │    File Storage       │
│  (Metadata & Logs)  │           │   (Model Artifacts)   │
└─────────────────────┘           └───────────────────────┘
```

### Stack công nghệ

| Tầng | Công nghệ | Mục đích |
|------|-----------|----------|
| **Frontend** | React 18, Tailwind CSS | Giao diện người dùng |
| **Biểu đồ** | Recharts | Line chart, Bar chart, Scatter plot |
| **Bảng dữ liệu** | TanStack Table | Filter, sort danh sách runs |
| **Backend** | Python 3.10+, FastAPI | REST API server |
| **ORM** | SQLAlchemy | Tương tác database |
| **Database** | PostgreSQL | Lưu trữ dữ liệu |
| **Auth** | JWT (JSON Web Token) | Xác thực người dùng |
| **File Storage** | Local filesystem | Lưu artifact (MVP) |

---

## Cấu trúc thư mục
 
```
experiment-tracking-system/
│
├── frontend/
│   ├── src/
│   │   ├── components/       # Chart, RunTable, Navbar, ...
│   │   ├── pages/            # LoginPage, DashboardPage, RunsPage, ...
│   │   ├── hooks/            # useExperiments, useRuns
│   │   ├── api.js            # tất cả hàm gọi API
│   │   └── App.jsx
│   └── package.json
│
├── backend/
│   ├── main.py               # FastAPI app
│   ├── database.py           # kết nối database
│   ├── models.py             # User, Experiment, Run, Metric
│   ├── schemas.py            # request/response schemas
│   ├── auth.py               # JWT helper
│   ├── routes/
│   │   ├── auth.py           # /register, /login
│   │   ├── experiments.py    # CRUD /experiments
│   │   ├── runs.py           # CRUD /runs
│   │   └── metrics.py        # /metrics
│   └── requirements.txt
│
├── README.md
└── .gitignore
```
 
---

---

##  Hướng dẫn cài đặt

### Yêu cầu hệ thống

- **OS**: Windows, Linux, macOS
- **Python**: 3.10+
- **Node.js**: 18+
- **PostgreSQL**: 14+

### Backend
 
```bash
cd backend
python -m venv venv
source venv/bin/activate        # Windows: venv\Scripts\activate
pip install -r requirements.txt
 
# Tạo file .env (xem .env.example)
cp .env.example .env
 
uvicorn main:app --reload
# API chạy tại: http://localhost:8000
# Swagger docs: http://localhost:8000/docs
```
 
### Frontend
 
```bash
cd frontend
npm install
npm run dev
# Giao diện chạy tại: http://localhost:3000
```

## ⚙️ Cấu hình
 
```env
DB_HOST=localhost
DB_PORT=5432
DB_USER=postgres
DB_PASSWORD=your_password
DB_NAME=experiment_tracker
SECRET_KEY=your_secret_key
```
 
---
---

## Tính năng
 
### MVP — hoàn thành 12/04/2026
- Đăng ký / Đăng nhập (JWT)
- Tạo, sửa, xóa Experiment
- Tạo Run, log hyperparameters & metrics
- Xem danh sách Run (filter, sort)
- Biểu đồ line chart so sánh metrics giữa các Run
- Biểu đồ bar chart so sánh best metric giữa các Run
- Phân quyền Viewer / Editor
 
### Beta — hoàn thành 10/05/2026
- Upload artifact (file model)
- Mời thành viên qua email
- Export kết quả CSV
 
---Scatter plot (learning_rate vs accuracy)

---

## Đóng góp

Mọi đóng góp đều được hoan nghênh! Để đóng góp:

1. Fork repository này
2. Tạo branch mới: `git checkout -b feature/ten-tinh-nang`
3. Commit thay đổi: `git commit -m 'feat: thêm tính năng X'`
4. Push lên branch: `git push origin feature/ten-tinh-nang`
5. Tạo Pull Request

## Các câu hỏi cho thầy

1. Về phạm vi dự án:

Với thời gian còn lại đến 12/04, nếu nhóm không kịp làm hết các tính năng MVP thì ưu tiên tính năng nào trước?
Phần upload artifact (file model) có bắt buộc trong MVP không, hay chỉ cần lưu thông tin params và metrics là đủ?

2. Về kỹ thuật:

Hệ thống có cần deploy lên server thật (có domain, public URL) hay chỉ cần demo được trên localhost là đủ?
Backend và frontend có bắt buộc tách riêng (REST API) không, hay có thể dùng fullstack như Next.js cho đơn giản hơn?

3. Về chấm điểm:

Tiêu chí chấm phần visualization/dashboard được đánh giá như thế nào — chú trọng số lượng chart hay tính hữu ích của dữ liệu hiển thị?
Phần kiểm thử (testing) cần ở mức nào — unit test đầy đủ hay chỉ cần test thủ công và có ghi lại kết quả?

4. Về báo cáo Beta:

Phần "viết báo cáo" ở Beta Version cần theo mẫu cụ thể nào không, hay tự do trình bày?

</div>
