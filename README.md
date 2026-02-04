# Carbon Sleuth 🕵️‍♂️

<div align="center">
  <img src="web-frontend/public/logo.png" alt="Carbon Sleuth Logo" width="200"/>
  <br>
  <em>Advanced Industrial Parameter Analysis & Anomaly Detection</em>
</div>

<br>

A hybrid Web and Desktop application for analyzing chemical equipment data with advanced analytics, outlier detection, and AI-powered insights.

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
| [Backend README](backend/README.md) | API endpoints, admin panel, deployment guide |
| [Web Frontend README](web-frontend/README.md) | User guide, Vercel deployment, usage |
| [Desktop Frontend README](desktop-frontend/README.md) | Installation, usage, features |

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

### 3. AI Features Setup (Optional)

To enable AI insights (OpenRouter), configure the frontend:

1.  Get an API Key from [OpenRouter.ai](https://openrouter.ai/).
2.  Create/Edit `web-frontend/.env`:
    ```env
    VITE_OPENROUTER_API_KEY=sk-or-v1-your-key-here...
    VITE_AI_MODEL=google/gemini-2.0-flash-lite-preview-02-05:free
    ```
3.  Restart the frontend server.

### 4. Desktop App Setup

```bash
cd desktop-frontend
pip install -r dict_requirements.txt # If distinct, otherwise uses root requirements
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
- **CSV Upload**: Drag & drop support
- **Real-time Processing**: Pandas-based statistical analysis
- **Advanced Analytics**:
  1. Outlier Detection (IQR method)
  2. Type Comparison Charts
  3. Correlation Matrix
  4. Health Status Classification
  5. **AI Insights**: Natural language analysis of equipment data

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

### Admin Panel

Visit: **http://127.0.0.1:8000/admin/**

---

## 📝 License

Developed as part of the FOSSEE internship screening task.
