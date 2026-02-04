# Carbon Sleuth - Backend Engine

Django REST Framework API serving as the core engine for Carbon Sleuth. Handles data processing, outlier detection algorithms, and PDF report generation.

## Table of Contents

- [Quick Start](#quick-start)
- [API Endpoints](#api-endpoints)
- [Configuration](#configuration)
- [Deployment](#deployment)
- [Troubleshooting](#troubleshooting)

---

## Quick Start

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

# Analytics Thresholds (optional)
WARNING_PERCENTILE=0.75
OUTLIER_IQR_MULTIPLIER=1.5
```

Initialize database:

```bash
python manage.py migrate
python manage.py initadmin
python manage.py runserver
```

Backend runs at: **http://127.0.0.1:8000**

---

## API Endpoints

### Authentication

| Method | Endpoint | Auth | Description |
|--------|----------|------|-------------|
| POST | `/api/register/` | No | Create new user account |
| POST | `/api/login/` | No | Get JWT access and refresh tokens |
| POST | `/api/token/refresh/` | No | Refresh expired access token |

### Data Operations

| Method | Endpoint | Auth | Description |
|--------|----------|------|-------------|
| POST | `/api/upload/` | Yes | Upload CSV file for analysis |
| GET | `/api/history/` | Yes | Get last 5 uploads (user-scoped) |
| GET | `/api/report/<id>/` | Yes | Download PDF report |
| GET | `/api/thresholds/` | Yes | Get current threshold settings |

**Authorization Header:** `Authorization: Bearer <access_token>`

---

## Configuration

### Health Status Thresholds

Equipment is classified into three health statuses based on `.env` settings:

| Status | Color | Criteria |
|--------|-------|----------|
| 🟢 **Normal** | Green | All parameters below warning threshold |
| 🟡 **Warning** | Yellow | Any parameter above `WARNING_PERCENTILE` (Default: 0.75) |
| 🔴 **Critical** | Red | Any parameter is an outlier based on `OUTLIER_IQR_MULTIPLIER` (Default: 1.5) |

---

## Deployment (Manual)

**Note:** Ensure you have SSH access to your server.

### 1. Update Code
```bash
cd ~/chemical_app
git pull origin main
```

### 2. Update Dependencies & Database
```bash
cd backend
source venv/bin/activate
pip install -r requirements.txt
python manage.py migrate
```

### 3. Restart Application (Gunicorn)
```bash
# Graceful reload
ps aux | grep gunicorn
kill -HUP <MASTER_PID>

# OR via Systemd
sudo systemctl restart gunicorn
```

---

## Troubleshooting

### "405 Method Not Allowed"
**Cause:** Server running old code.
**Fix:** Restart Gunicorn/Application server.

### "OperationalError: no such table"
**Cause:** Pending migrations.
**Fix:** Run `python manage.py migrate`.
