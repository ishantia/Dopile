# Dopile — Secure LAN Task Manager Server for Android/Termux

**Dopile** is a production-quality, self-hosted, multi-user **LAN Task Manager** designed specifically to run as a lightweight web server on an **Android phone using Termux**, without requiring Docker, root access, Android Studio, or an Android APK.

The Android phone acts as the server. Any device connected to the same Wi-Fi network, local area network (LAN), or mobile Wi-Fi hotspot can access Dopile through a browser or install it as a Progressive Web App (PWA).

---

## 1. Architecture

```text
Android Phone (Termux)
└── Python 3 + FastAPI + Uvicorn
    ├── REST API (/api/auth, /api/tasks, /api/users, /api/admin)
    ├── Realtime WebSockets (/ws)
    ├── Security (Argon2id, HttpOnly Cookies, CSRF, Rate Limiting)
    ├── SQLite WAL Database (SQLAlchemy 2.0 + Alembic)
    └── Static SPA / PWA Serving
```

### Stack & Components

- **Backend**: Python 3, FastAPI, Uvicorn, SQLAlchemy 2.0 (SQLite WAL mode), Alembic, Argon2id (`argon2-cffi`), PyJWT, Pydantic v2, Pytest.
- **Frontend**: React 18, TypeScript, Vite, Tailwind CSS, Lucide icons, Installable PWA Service Worker.

---

## 2. Core Features

- 🔐 **Secure Authentication**: Argon2id password hashing, HttpOnly cookies, SameSite protection, double-submit CSRF tokens, session expiration, and login rate-limiting (brute force protection).
- 🛡️ **Role-Based Authorization**: Strict resource scoping (`USER` vs `ADMIN`). Prevention of IDOR and privilege escalation vulnerabilities.
- 📋 **Task Management**: Create, search, filter by status/priority, sort, set due dates, and update tasks.
- ⚡ **Realtime Synchronization**: Authenticated WebSocket broadcasts for instant task status updates across connected devices.
- 👑 **Admin Console**: User management (create users, deactivate accounts, reset passwords, change roles), system audit logs, live server telemetry, and database backup/restore.
- 📱 **PWA & Mobile-First UX**: Responsive mobile layout with offline static asset caching.
- 📦 **Termux Native**: Simple shell scripts (`start.sh`, `stop.sh`, `status.sh`) and CLI management without complex container runtimes.

---

## 3. Termux Installation Guide

### Step 1: Install Termux Packages & Build Tools

Open Termux on your Android device and install Python, Git, and build toolchain (required for compiled C/Rust extensions on Android):

```bash
pkg update && pkg upgrade -y
pkg install python git clang rust binutils make -y
```

### Step 2: Clone & Setup Environment

Clone the repository and install dependencies:

```bash
git clone https://github.com/ishantia/Dopile.git
cd Dopile

# Create virtual environment
python -m venv .venv
source .venv/bin/activate

# Install Python requirements
pip install -r backend/requirements.txt
```

### Step 3: Build Frontend PWA (Optional if pre-built)

If building from source on Termux (requires Node.js):

```bash
pkg install nodejs -y
cd frontend
npm install
npm run build
cd ..
```

### Step 4: Initialize Server & Create Admin

Run the CLI initialization script to generate secure `.env` secrets and initialize database tables:

```bash
PYTHONPATH=backend python -m app.cli init
```

Create your administrative account:

```bash
PYTHONPATH=backend python -m app.cli create-admin --username admin
```

### Step 5: Start Server

Make scripts executable and run:

```bash
chmod +x start.sh stop.sh status.sh
./start.sh
```

Sample output:

```text
Dopile
────────────────────────
Status:   RUNNING

Local:    http://localhost:8080
LAN:      http://192.168.1.50:8080
Port:     8080
Database: OK
PWA:      READY
────────────────────────
Press Ctrl+C to stop server.
```

---

## 4. Android Battery Optimization Notice

To prevent Android OS power management from killing the Termux background server:

1. Open Android **Settings** &rarr; **Apps** &rarr; **Termux**.
2. Set Battery Usage to **Unrestricted** / **Don't Optimize**.
3. In Termux, run `termux-wake-lock` to keep the CPU awake during active server operations.

---

## 5. Security Model & Best Practices

- **Argon2id Hashing**: Passwords are never stored in plaintext. Argon2id protects against hardware-accelerated dictionary attacks.
- **Double-Submit CSRF Protection**: State-changing endpoints (`POST`, `PUT`, `PATCH`, `DELETE`) require a valid `X-CSRF-Token` matching the user session.
- **No Database Expose**: SQLite database file (`data/dopile.db`) is stored strictly outside the public web root.
- **Audit Logging**: All security actions (`LOGIN_SUCCESS`, `PASSWORD_RESET`, `USER_DISABLED`, `BACKUP_CREATED`) are logged into a queryable audit table.

---

## 6. Running Automated Tests

Run the backend pytest suite:

```bash
cd backend
pytest -v
```

---

## 7. License

MIT License. Designed and built for self-hosted LAN productivity.
