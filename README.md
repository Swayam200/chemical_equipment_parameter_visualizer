# Chemical Equipment Parameter Visualizer

A hybrid Web and Desktop application for analyzing chemical equipment data.

## Project Structure

- `backend/`: Django REST Framework API
- `web-frontend/`: React + Vite + Chart.js
- `desktop-frontend/`: PyQt5 + Matplotlib

## Setup Instructions

### Prerequisites

- Python 3.8+
- Node.js & npm

### 1. Backend Setup

#### Step 1: Create and Activate Virtual Environment

```bash
cd backend
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

#### Step 2: Install Dependencies

```bash
pip install -r requirements.txt
# Or manually: pip install django djangorestframework pandas matplotlib reportlab django-cors-headers python-dotenv
```

#### Step 3: Configure Environment Variables

Create a `.env` file in the `backend/` directory with the following:

```env
DEBUG=True
SECRET_KEY=your-secret-key-here
ALLOWED_HOSTS=127.0.0.1,localhost
CORS_ALLOWED_ORIGINS=http://localhost:5173
ADMIN_USERNAME=admin
ADMIN_PASSWORD=your_secure_password_here
ADMIN_EMAIL=admin@example.com
```

**Important:** Change `ADMIN_PASSWORD` to a secure password of your choice. This will be your admin login credentials.

#### Step 4: Run Migrations

```bash
python manage.py migrate
```

#### Step 5: Create Admin User

```bash
python manage.py initadmin
```

This command reads credentials from your `.env` file and creates/updates the superuser account.

#### Step 6: Start the Development Server

```bash
python manage.py runserver
```

_The API will run at http://127.0.0.1:8000/_

**To change admin password later:** Simply update `ADMIN_PASSWORD` in `.env` and run `python manage.py initadmin` again.

### 2. Web Frontend Setup

```bash
cd web-frontend
npm install
npm run dev
```

_The Web App will run at http://localhost:5173/_

### 3. Desktop App Setup

Ensure the backend is running first.

```bash
cd desktop-frontend
# Ensure pandas, pyqt5, requests, matplotlib are installed in your python environment
python main.py
```

## Features

- **User Authentication**: Register and login with JWT tokens
- **CSV Upload**: Drag & Drop (Web) or File Dialog (Desktop)
- **Dashboard**: Interactive Charts and Statistics
- **History**: View last 5 uploads
- **PDF Report**: Generate downloadable reports (Web)

## User Authentication

### For Regular Users

Both Web and Desktop applications support user registration and login:

**Web Frontend:**

1. Visit http://localhost:5173/
2. Click "Register" to create a new account
3. Fill in username, email, and password (min 8 characters)
4. After registration, you'll be automatically logged in

**Desktop Frontend:**

1. Launch the desktop app: `python main.py`
2. Click "Don't have an account? Register"
3. Fill in the registration form
4. After successful registration, switch to login and enter credentials

### For Admin Users

Admin credentials are configured through the `.env` file in the `backend/` directory:

- **Username:** Value of `ADMIN_USERNAME` (default: `admin`)
- **Password:** Value of `ADMIN_PASSWORD` (set by you)
- **Email:** Value of `ADMIN_EMAIL` (default: `admin@example.com`)

**First Time Setup:** Run `python manage.py initadmin` after configuring your `.env` file.

**Updating Admin Password:** Edit `ADMIN_PASSWORD` in `.env` and run `python manage.py initadmin` again.

### Viewing Registered Users

Access the Django Admin Panel to manage users:

```bash
# Start the backend server
cd backend
source venv/bin/activate
python manage.py runserver

# Visit: http://127.0.0.1:8000/admin/
# Login with admin credentials from .env
# Navigate to "Users" section to view/manage all registered users
```

### Resetting the Database

To clear all users and data:

```bash
cd backend
rm db.sqlite3
rm -rf media/uploads/*
python manage.py migrate
python manage.py initadmin
```

## API Endpoints

- `POST /api/register/` - Register new user
- `POST /api/login/` - Login and get JWT tokens
- `POST /api/upload/` - Upload CSV file (requires authentication)
- `GET /api/history/` - Get upload history (requires authentication)
- `GET /api/uploads/<id>/` - Get specific upload details
- `GET /api/report/<id>/` - Generate PDF report
