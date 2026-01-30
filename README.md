# Chemical Equipment Parameter Visualizer

A hybrid Web and Desktop application for analyzing chemical equipment data with advanced analytics, outlier detection, and health status monitoring.

![Version](https://img.shields.io/badge/version-1.1.0-blue)
![Python](https://img.shields.io/badge/python-3.8+-green)
![React](https://img.shields.io/badge/react-18-blue)
![Django](https://img.shields.io/badge/django-5.0-green)

## 📋 Project Structure

```
├── backend/           # Django REST Framework API
├── web-frontend/      # React + Vite + Chart.js web app
└── desktop-frontend/  # PyQt5 + Matplotlib desktop app
```

**📖 Detailed Documentation:**

| Component | Description |
|-----------|-------------|
| [Backend README](backend/README.md) | API endpoints, admin panel, threshold configuration |
| [Web Frontend README](web-frontend/README.md) | Features, user guide, chart interactions |
| [Desktop Frontend README](desktop-frontend/README.md) | Features, toolbar usage, platform notes |
| [Threshold Configuration](backend/threshold_config.md) | In-depth threshold customization guide |

---

## ⚡ Quick Start

### Prerequisites

- Python 3.8+
- Node.js & npm (for web frontend)

### 1. Backend Setup

```bash
cd backend
python3 -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
pip install -r requirements.txt
```

Create `.env` file:

```env
DEBUG=True
SECRET_KEY=your-secret-key-here
ADMIN_USERNAME=admin
ADMIN_PASSWORD=your_secure_password
ADMIN_EMAIL=admin@example.com
CORS_ALLOWED_ORIGINS=http://localhost:5173
```

Initialize database:

```bash
python manage.py migrate
python manage.py initadmin
python manage.py runserver
```

Backend runs at: **http://127.0.0.1:8000**

### 2. Web Frontend Setup

```bash
cd web-frontend
npm install
npm run dev
```

Web app runs at: **http://localhost:5173**

### 3. Desktop App Setup

```bash
cd desktop-frontend
pip install -r requirements.txt
python main.py
```

---

## 🎯 Key Features

### User Authentication
- JWT-based authentication with automatic token refresh
- Register/Login with form validation
- Per-user data isolation

### Data Analysis
- **CSV Upload**: Drag & drop with 5 MB limit, progress bar
- **Real-time Processing**: Pandas-based statistical analysis
- **5 Advanced Analytics**:
  1. Outlier Detection (IQR method)
  2. Type Comparison Charts
  3. Correlation Matrix
  4. Enhanced Statistics
  5. Health Status Classification

### Interactive Visualizations
- **Web**: Chart.js with zoom/pan, enhanced tooltips
- **Desktop**: Matplotlib with navigation toolbar
- **PDF Reports**: Professional styled reports with charts

### Health Status System

| Status | Color | Criteria |
|--------|-------|----------|
| 🟢 Normal | Green | Parameters within normal range |
| 🟡 Warning | Yellow | Parameters above 75th percentile |
| 🔴 Critical | Red | Parameters are statistical outliers |

---

## 🔧 Configuration

### Analytics Thresholds

Edit `backend/.env`:

```env
# Warning: Top 25% get yellow status (0.5 - 0.95)
WARNING_PERCENTILE=0.75

# Critical: Standard outlier detection (0.5 - 3.0)
OUTLIER_IQR_MULTIPLIER=1.5
```

**Note:** Restart backend after changes. Old uploads auto-recalculate with new thresholds!

See [Threshold Configuration Guide](backend/threshold_config.md) for detailed examples.

### Admin Panel

Visit: **http://127.0.0.1:8000/admin/**

Use credentials from `.env` to manage users and uploads.

---

## 📊 API Endpoints

| Method | Endpoint | Auth | Description |
|--------|----------|------|-------------|
| POST | `/api/register/` | No | Create account |
| POST | `/api/login/` | No | Get JWT tokens |
| POST | `/api/token/refresh/` | No | Refresh token |
| POST | `/api/upload/` | Yes | Upload CSV |
| GET | `/api/history/` | Yes | Last 5 uploads |
| GET | `/api/report/<id>/` | Yes | Download PDF |

**Auth Header:** `Authorization: Bearer <token>`

---

## 🧪 Sample Data Format

```csv
Equipment Name,Type,Flowrate,Pressure,Temperature
Pump-001,Pump,45.2,150.5,75.3
Reactor-A1,Reactor,120.0,300.0,185.0
```

**Required columns:**
- Equipment Name (string)
- Type (string)
- Flowrate, Pressure, Temperature (numeric)

---

## 🐛 Troubleshooting

| Issue | Solution |
|-------|----------|
| Port 8000 in use | `lsof -ti:8000 | xargs kill -9` |
| CORS errors | Check `CORS_ALLOWED_ORIGINS` in `.env` |
| Charts not rendering | Check browser console / reinstall npm packages |
| Desktop connection error | Ensure backend is running |

See individual README files for detailed troubleshooting.

---

## 📦 Tech Stack

### Backend
- Django 5.0 + REST Framework
- SimpleJWT authentication
- Pandas, ReportLab, Matplotlib

### Web Frontend
- React 18 + Vite
- Chart.js with zoom plugin
- Axios with auto-refresh

### Desktop Frontend
- PyQt5
- Matplotlib with interactive toolbar
- Requests

---

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Commit your changes
4. Push to the branch
5. Open a Pull Request

---

## 📝 License

Developed as part of the FOSSEE internship screening task.

---

**Version:** 1.1.0  
**Last Updated:** January 2026
