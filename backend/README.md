# Backend - Chemical Equipment Parameter Visualizer

Django REST Framework API with JWT authentication, data processing, and PDF report generation.

## Table of Contents

- [Quick Start](#quick-start)
- [API Endpoints](#api-endpoints)
- [Admin Panel](#admin-panel)
- [Configuration](#configuration)
- [Health Status Thresholds](#health-status-thresholds)
- [PDF Reports](#pdf-reports)
- [Database Management](#database-management)
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

**Register Request:**
```json
{
  "username": "user1",
  "email": "user@example.com",
  "password": "securepass123"
}
```

**Login Response:**
```json
{
  "access": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9...",
  "refresh": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9..."
}
```

### Data Operations

| Method | Endpoint | Auth | Description |
|--------|----------|------|-------------|
| POST | `/api/upload/` | Yes | Upload CSV file for analysis |
| GET | `/api/history/` | Yes | Get last 5 uploads (user-scoped) |
| GET | `/api/uploads/<id>/` | Yes | Get specific upload details |
| GET | `/api/report/<id>/` | GET | Download PDF report |
| GET | `/api/thresholds/` | Yes | Get current threshold settings |

**Authorization Header:**
```
Authorization: Bearer <access_token>
```

### Upload Response

```json
{
  "id": 5,
  "user_upload_index": 3,
  "file": "uploads/equipment_data.csv",
  "uploaded_at": "2026-01-30T10:30:00Z",
  "summary": {
    "total_count": 50,
    "average_flowrate": 45.2,
    "average_pressure": 150.5,
    "average_temperature": 75.3,
    "type_counts": {"Pump": 20, "Reactor": 15, "Valve": 15},
    "outliers": [...]
  },
  "processed_data": [
    {
      "Equipment Name": "Pump-001",
      "Type": "Pump",
      "Flowrate": 45.2,
      "Pressure": 150.5,
      "Temperature": 75.3,
      "health_status": "normal",
      "health_color": "#10b981"
    }
  ]
}
```

### Error Responses

```json
{
  "error": "File too large. Maximum allowed size is 5 MB."
}
```

```json
{
  "error": "Missing required columns: Equipment Name, Type"
}
```

---

## Admin Panel

### Access

1. Visit: **http://127.0.0.1:8000/admin/**
2. Login with credentials from `.env`

### Available Actions

- **View all users**: Authentication → Users
- **View all uploads**: API → Uploaded files
- **Create/edit/delete users**
- **Change passwords**
- **Manage permissions**

### Updating Admin Password

```bash
# Edit .env file
ADMIN_PASSWORD=new_password

# Update admin user
python manage.py initadmin
```

---

## Configuration

### Environment Variables

| Variable | Description | Default |
|----------|-------------|---------|
| `DEBUG` | Enable debug mode | `True` |
| `SECRET_KEY` | Django secret key | *required* |
| `ALLOWED_HOSTS` | Allowed host domains | `127.0.0.1,localhost` |
| `CORS_ALLOWED_ORIGINS` | CORS origins for frontend | `http://localhost:5173` |
| `ADMIN_USERNAME` | Initial admin username | `admin` |
| `ADMIN_PASSWORD` | Initial admin password | *required* |
| `ADMIN_EMAIL` | Initial admin email | `admin@example.com` |
| `WARNING_PERCENTILE` | Warning threshold | `0.75` |
| `OUTLIER_IQR_MULTIPLIER` | Outlier detection multiplier | `1.5` |

---

## Health Status Thresholds

### Overview

Equipment is classified into three health statuses:

| Status | Color | Criteria |
|--------|-------|----------|
| 🟢 **Normal** | Green (#10b981) | All parameters below warning threshold |
| 🟡 **Warning** | Yellow (#f59e0b) | Any parameter above warning threshold |
| 🔴 **Critical** | Red (#ef4444) | Any parameter is a statistical outlier |

### Configuration

Edit `backend/.env`:

```env
# Warning: Flag equipment in top 25%
WARNING_PERCENTILE=0.75

# Critical: Standard IQR outlier detection
OUTLIER_IQR_MULTIPLIER=1.5
```

### Threshold Examples

**Scenario: More strict warnings (flag top 30%)**
```env
WARNING_PERCENTILE=0.70
```

**Scenario: Less strict warnings (flag top 15%)**
```env
WARNING_PERCENTILE=0.85
```

**Scenario: More sensitive outlier detection**
```env
OUTLIER_IQR_MULTIPLIER=1.0
```

**Scenario: Less sensitive outlier detection**
```env
OUTLIER_IQR_MULTIPLIER=2.0
```

### Common Configurations

| Use Case | Warning | IQR | Description |
|----------|---------|-----|-------------|
| Default | 0.75 | 1.5 | Balanced detection |
| Safety-Critical | 0.70 | 1.0 | Catch issues early |
| Exploratory | 0.85 | 2.0 | Minimize alerts |

### Apply Changes

```bash
# Restart server after changing .env
python manage.py runserver
```

**Auto-recalculation**: Old uploads automatically recalculate when viewed with new thresholds!

---

## PDF Reports

### Features

- Professional header with title and accent line
- Summary statistics with styled metadata box
- Type distribution pie chart
- Complete data table with color-coded health status
- Outlier alert section
- Page numbers on all pages
- Consistent footer across pages

### Customization

PDF styling is defined in `api/views.py` in the `PDFReportView` class:

```python
COLORS = {
    'primary': HexColor('#1a1a2e'),
    'accent': HexColor('#0f3460'),
    'highlight': HexColor('#e94560'),
    'success': HexColor('#10b981'),
    'warning': HexColor('#f59e0b'),
    'danger': HexColor('#ef4444'),
}
```

---

## Database Management

### Reset Database

```bash
cd backend
rm db.sqlite3
rm -rf media/uploads/*
python manage.py migrate
python manage.py initadmin
```

### Backup Database

```bash
cp db.sqlite3 db.sqlite3.backup.$(date +%Y%m%d)
```

### View Data via Shell

```bash
python manage.py shell
```

```python
from api.models import UploadedFile
from django.contrib.auth.models import User

# List users
User.objects.all().values('id', 'username', 'email')

# List uploads
UploadedFile.objects.all()
```

### Fix Upload Numbering

If upload numbers are inconsistent:

```bash
python manage.py shell
```

```python
from api.models import UploadedFile
from django.contrib.auth.models import User

for user in User.objects.all():
    uploads = UploadedFile.objects.filter(user=user).order_by('uploaded_at')
    for idx, upload in enumerate(uploads, start=1):
        upload.user_upload_index = idx
        upload.save(update_fields=['user_upload_index'])
print("Fixed!")
```

---

## Troubleshooting

### Port 8000 already in use

```bash
lsof -ti:8000 | xargs kill -9
# Or use different port
python manage.py runserver 8001
```

### Migration errors

```bash
python manage.py migrate --run-syncdb
```

### Admin login not working

```bash
python manage.py initadmin
```

### CORS errors on frontend

Check `.env`:
```env
CORS_ALLOWED_ORIGINS=http://localhost:5173
```

Restart server after changes.

### Database locked

```bash
pkill -f runserver
python manage.py runserver
```

---

## Security Notes

- ⚠️ Never commit `.env` to version control
- ⚠️ Change default admin password in production
- ⚠️ Set `DEBUG=False` in production
- ⚠️ Use strong `SECRET_KEY`
- ⚠️ Configure `ALLOWED_HOSTS` properly
- ⚠️ Use HTTPS in production

---

## Dependencies

```
Django>=5.0
djangorestframework>=3.15
djangorestframework-simplejwt>=5.3
pandas>=2.0
reportlab>=4.0
python-dotenv>=1.0
django-cors-headers>=4.3
matplotlib>=3.8
pytz>=2024.1
```

Install:
```bash
pip install -r requirements.txt
```
