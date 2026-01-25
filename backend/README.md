# Backend Administration Guide

This guide covers administrative tasks for managing the Django backend.

## Table of Contents

- [Admin Panel Access](#admin-panel-access)
- [Managing Users](#managing-users)
- [Database Management](#database-management)
- [Environment Configuration](#environment-configuration)

---

## Admin Panel Access

### Accessing Django Admin

The Django admin panel provides a web interface to manage users, uploads, and other database objects.

**Steps:**

1. Ensure the backend server is running:

   ```bash
   cd backend
   source venv/bin/activate
   python manage.py runserver
   ```

2. Visit the admin panel:

   ```
   http://127.0.0.1:8000/admin/
   ```

3. Login with admin credentials from your `.env` file:
   - **Username:** Value of `ADMIN_USERNAME` (default: `admin`)
   - **Password:** Value of `ADMIN_PASSWORD` (set in `.env`)

### What You Can Do in Admin Panel

- **View all registered users** (Users section)
- **View all uploads** (Uploaded files section)
- **Create/edit/delete users**
- **View user details** (email, join date, last login, etc.)
- **Change passwords**
- **Manage user permissions** (staff status, superuser status)

---

## Managing Users

### Viewing User List

**Option 1: Django Admin Panel** (Recommended)

1. Visit http://127.0.0.1:8000/admin/
2. Login with admin credentials
3. Click on "Users" under Authentication and Authorization
4. You'll see a complete list of all registered users with:
   - Username
   - Email
   - Staff status
   - Active status
   - Date joined

**Option 2: Django Shell**

```bash
cd backend
source venv/bin/activate
python manage.py shell
```

```python
from django.contrib.auth.models import User

# List all users
users = User.objects.all()
for u in users:
    print(f"ID: {u.id} | Username: {u.username} | Email: {u.email}")
    print(f"   Superuser: {u.is_superuser} | Staff: {u.is_staff}")
    print(f"   Date Joined: {u.date_joined}")
    print(f"   Last Login: {u.last_login}")
    print()

# Count total users
print(f"Total users: {User.objects.count()}")

# Exit shell
exit()
```

**Option 3: Direct SQLite Query**

```bash
cd backend
sqlite3 db.sqlite3
```

```sql
-- View all users
SELECT id, username, email, is_superuser, date_joined FROM auth_user;

-- Count users
SELECT COUNT(*) FROM auth_user;

-- Exit SQLite
.quit
```

### Viewing User Uploads

Each user's uploads are isolated. To view uploads per user:

```python
from django.contrib.auth.models import User
from api.models import UploadedFile

# Get a specific user
user = User.objects.get(username='testuser')

# View their uploads
uploads = UploadedFile.objects.filter(user=user)
for upload in uploads:
    print(f"ID: {upload.id} | File: {upload.file.name}")
    print(f"   Uploaded: {upload.uploaded_at}")
    print(f"   Records: {upload.summary.get('total_count', 0)}")
    print()
```

### Deleting a Specific User

**Via Admin Panel:**

1. Go to http://127.0.0.1:8000/admin/
2. Click "Users"
3. Select the user you want to delete
4. Choose "Delete selected users" from the action dropdown
5. Confirm deletion

**Note:** Deleting a user will also delete all their uploads (cascade delete).

---

## Database Management

### Resetting the Entire Database

If you want to start fresh (delete all users, uploads, and data):

```bash
cd backend

# 1. Delete the database file
rm db.sqlite3

# 2. Delete all uploaded files
rm -rf media/uploads/*

# 3. Recreate database tables
source venv/bin/activate
python manage.py migrate

# 4. Recreate admin user
python manage.py initadmin
```

**Warning:** This will permanently delete:

- All registered users (except admin which will be recreated)
- All uploaded CSV files
- All upload history and statistics

### Resetting Only User Data (Keep Structure)

To delete all users except admin:

```bash
cd backend
source venv/bin/activate
python manage.py shell
```

```python
from django.contrib.auth.models import User
from api.models import UploadedFile

# Delete all uploads
UploadedFile.objects.all().delete()
print("All uploads deleted")

# Delete all non-superuser users
non_admin_users = User.objects.filter(is_superuser=False)
count = non_admin_users.count()
non_admin_users.delete()
print(f"Deleted {count} regular users")

exit()
```

### Backing Up the Database

```bash
cd backend

# Create backup
cp db.sqlite3 db.sqlite3.backup.$(date +%Y%m%d_%H%M%S)

# List backups
ls -lh db.sqlite3.backup.*
```

### Restoring from Backup

```bash
cd backend

# List available backups
ls -lh db.sqlite3.backup.*

# Restore (replace YYYYMMDD_HHMMSS with your backup timestamp)
cp db.sqlite3.backup.YYYYMMDD_HHMMSS db.sqlite3
```

---

## Environment Configuration

### Updating Admin Credentials

To change the admin password:

1. Edit `backend/.env` file:

   ```env
   ADMIN_PASSWORD=new_secure_password_here
   ```

2. Update the admin user:
   ```bash
   cd backend
   source venv/bin/activate
   python manage.py initadmin
   ```

### Environment Variables

The backend uses the following environment variables (stored in `.env`):

| Variable               | Description                   | Default                 |
| ---------------------- | ----------------------------- | ----------------------- |
| `DEBUG`                | Enable debug mode             | `True`                  |
| `SECRET_KEY`           | Django secret key             | (required)              |
| `ALLOWED_HOSTS`        | Comma-separated allowed hosts | `127.0.0.1,localhost`   |
| `CORS_ALLOWED_ORIGINS` | CORS origins for frontend     | `http://localhost:5173` |
| `ADMIN_USERNAME`       | Initial admin username        | `admin`                 |
| `ADMIN_PASSWORD`       | Initial admin password        | (required)              |
| `ADMIN_EMAIL`          | Initial admin email           | `admin@example.com`     |

---

## Troubleshooting

### "Admin login not working"

- Verify credentials in `.env` file
- Run `python manage.py initadmin` to update admin password
- Check if admin user exists: `python manage.py shell` → `User.objects.filter(username='admin').exists()`

### "Database is locked"

- Stop all running servers: `pkill -f runserver`
- Close any open database connections
- Restart the development server

### "Uploads not showing"

- Uploads are per-user. Make sure you're logged in as the user who uploaded
- Check if files exist: `ls -lh media/uploads/`
- Verify user association: Check admin panel → Uploaded files

### "Migration errors"

If you encounter migration conflicts:

```bash
cd backend
rm db.sqlite3
rm api/migrations/0*.py
python manage.py makemigrations
python manage.py migrate
python manage.py initadmin
```

---

## Quick Reference Commands

```bash
# Start server
python manage.py runserver

# Create admin user
python manage.py initadmin

# Open Django shell
python manage.py shell

# Create migrations
python manage.py makemigrations

# Apply migrations
python manage.py migrate

# Reset database
rm db.sqlite3 && python manage.py migrate && python manage.py initadmin

# View logs in SQLite
sqlite3 db.sqlite3 "SELECT * FROM api_uploadedfile;"
```

---

## Security Notes

- **Never commit `.env` file** to version control
- **Change default admin password** before deployment
- **Disable DEBUG** in production (`DEBUG=False`)
- **Use strong SECRET_KEY** for production
- **Configure ALLOWED_HOSTS** properly for production
- **Use HTTPS** in production environments
