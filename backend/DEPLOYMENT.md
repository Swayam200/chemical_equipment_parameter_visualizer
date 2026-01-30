# Backend Deployment & Maintenance Guide

This guide describes how to manually update the production backend API running on a VPS or Cloud Instance (e.g., Oracle Cloud, AWS EC2, DigitalOcean).

**Note:** This guide documents the *process*. It does not contain private keys, IP addresses, or user credentials. Keep those secure in your local `.env` files or password manager.

## 🚀 Standard Update Procedure

Whenever new code is pushed to the `main` branch (e.g., new features, database changes, or bug fixes), the production server must be manually updated.

**Prerequisites:**
- SSH access to the server.
- The project is located at `~/chemical_app/backend` (or your specific path).
- The virtual environment is named `venv`.

### 1. Connect to the Server
SSH into your instance:
```bash
ssh ubuntu@<YOUR_SERVER_IP>
```

### 2. Pull Latest Code
Navigate to the project root and pull changes:
```bash
cd ~/chemical_app
git stash   # Safely stash local config changes (like settings.py)
git pull origin main
git stash pop  # Re-apply your local config
```
*Tip: If `git stash pop` shows conflicts, resolve them by ensuring your production `settings.py` keeps its specific configurations (e.g., `DEBUG=False`, `ALLOWED_HOSTS`).*

### 3. Update Database (Running Migrations)
**Crucial Step:** If the update involves new models (like `UserThresholdSettings`), you **MUST** run migrations.

```bash
cd backend
source venv/bin/activate
python manage.py migrate
```

### 4. Restart the Application Server (Gunicorn)
The running application has the *old code* loaded in memory. You must restart/reload it to see changes.

#### Option A: Using Systemd (Recommended if service exists)
If a systemd service is configured (check `/etc/systemd/system/`), restart it:
```bash
sudo systemctl restart gunicorn
# OR
sudo systemctl restart chemical_app
```

#### Option B: Graceful Reload via PID (Universal Method)
If you cannot find the service name, or just want a zero-downtime reload:

1. **Find the Master Process ID (PID):**
   ```bash
   ps aux | grep gunicorn
   ```
   *Look for the process listing `gunicorn: master`.*

2. **Send HUP Signal (Reload):**
   Use the PID found in step 1 (e.g., `12345`):
   ```bash
   kill -HUP 12345
   ```
   *This forces Gunicorn to reload the code and configuration without dropping active connections.*

---

## 🔧 Troubleshooting

### "405 Method Not Allowed" after Deployment
**Symptom:** You added a new API method (e.g., `PUT`), verified it locally, but the production server rejects it with "Method Not Allowed".
**Cause:** The server is still running the old code in memory.
**Fix:** Perform **Step 4 (Restart)** above.

### "OperationalError: no such table"
**Symptom:** 500 Server Error when accessing new features.
**Cause:** Database migrations were not applied.
**Fix:** Perform **Step 3 (Migrate)** above.
