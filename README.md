# Experiment Tracking System

> Đồ án môn **Phát triển Ứng dụng** — Học kỳ 2, năm học 2025–2026  
> Giảng viên hướng dẫn: `<tên thầy/cô>`

---

## Giới thiệu

**Experiment Tracking System** là ứng dụng web giúp người dùng theo dõi, quản lý và so sánh các thí nghiệm machine learning một cách trực quan — thay thế việc ghi chép thủ công bằng Excel hay ghi chú rời rạc.

Người dùng tạo **Experiment** (dự án), bên trong chứa nhiều **Run** (lần chạy thử). Mỗi Run lưu lại hyperparameters, metrics theo từng epoch và hiển thị biểu đồ so sánh kết quả giữa các lần thử.

---

## Thành viên nhóm

| Họ tên | MSSV | Vai trò |
|--------|------|---------|
| `<họ tên>` | `<msv>` | Frontend |
| `<họ tên>` | `<msv>` | Frontend |
| `<họ tên>` | `<msv>` | Backend |
| `<họ tên>` | `<msv>` | Backend |

---

## Công nghệ sử dụng

| Tầng | Công nghệ |
|------|-----------|
| Frontend | React, Tailwind CSS, Recharts |
| Backend | Python, FastAPI |
| Database | PostgreSQL |
| Auth | JWT |

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

## Hướng dẫn chạy

### Yêu cầu
- Python 3.10+
- Node.js 18+
- PostgreSQL 14+

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

### Cấu hình `.env`

```env
DB_HOST=localhost
DB_PORT=5432
DB_USER=postgres
DB_PASSWORD=your_password
DB_NAME=experiment_tracker
SECRET_KEY=your_secret_key
```

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

---

## Giấy phép

MIT License — dự án học thuật, không dùng cho mục đích thương mại.
