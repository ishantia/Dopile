# Dopile 📋

**Secure, Self-Hosted LAN Task Manager Server for Android (Termux) & Linux**

Dopile is a modern, high-performance, self-hosted Task Manager application designed to run effortlessly on Android devices via Termux or any Linux server on your Local Area Network (LAN). It provides real-time task synchronization over WebSockets, Progressive Web App (PWA) offline capabilities, enterprise-grade security, and a full Admin Oversight Suite.

---

## 🌟 Key Features

* **📱 Progressive Web App (PWA)**: Installable on Android, iOS, Windows, and macOS as a native-feeling app with offline caching and service worker support.
* **⚡ Real-Time WebSocket Synchronization**: Live updates across all connected LAN devices whenever tasks are created, edited, re-prioritized, or completed.
* **🔒 Enterprise Security Architecture**:
  * **Argon2id Hashing**: High-security password hashing with salt.
  * **HttpOnly Session Cookies**: Prevents XSS token theft.
  * **Double-Submit CSRF Protection**: Strict `X-CSRF-Token` header verification for state-changing HTTP requests.
  * **Sliding-Window Rate Limiting**: In-memory rate limiting to prevent brute-force login attempts.
  * **Strict RBAC & IDOR Prevention**: Robust authorization checks enforcing user isolation and role permissions.
* **🌐 Per-Account Wi-Fi IP-Binding Security**:
  * **Standard Users (`USER`)**: Automatically bound to their Wi-Fi / LAN IP address upon first login or registration. Attempts to access an account from an unauthorized IP are blocked with HTTP 403.
  * **Admin Exemption (`ADMIN`)**: Admin accounts bypass IP binding restrictions and can log in from any IP address across the network.
  * **Admin Management**: Admins can view every user's bound IP, manually assign a new IP, or reset (unbind) a user's IP in the Admin Panel.
* **👑 Complete Admin Suite**:
  * **User Management**: Create users, toggle active status, update roles, reset passwords, delete accounts, and manage bound IP addresses.
  * **Task Oversight & Reassignment**: Inspect and reassign any task in the system.
  * **Audit Logging**: Comprehensive, immutable audit trail for security events, logins, and administrative actions.
  * **System Telemetry**: Live server status, active WebSocket connection counters, uptime, and database health metrics.
  * **Automated SQLite Backups**: One-click database backup and point-in-time restore functionality.
* **🤖 Termux & ARM64 Optimized**: Specifically engineered to bypass worker thread memory crashes during PWA minification on ARM/Android devices.

---

## 🛠️ Security & Architecture

| Layer | Mechanism | Details |
| :--- | :--- | :--- |
| **Authentication** | Argon2id + JWT HttpOnly Cookies | Passwords hashed with Argon2id ($m=65536, t=3, p=4$). Session tokens stored in HttpOnly, SameSite cookies. |
| **CSRF Defense** | Double-Submit Cookie Pattern | State-changing requests (`POST`, `PUT`, `PATCH`, `DELETE`) require a valid `X-CSRF-Token` header. |
| **IP Security** | Wi-Fi / LAN IP Binding | Accounts automatically bind to initial client IP. Admin bypass allows seamless administration. |
| **Data Storage** | SQLite Write-Ahead Logging (WAL) | High-concurrency SQLite storage with WAL mode enabled and foreign keys enforced. |
| **API Transport** | Dynamic Scheme Cookie Safety | Automatically adapts cookie `Secure` flag based on HTTP vs HTTPS scheme for seamless LAN access. |

---

## 🚀 Quick Start Guide for Termux / Linux

### 1. Prerequisites (Termux Setup)

On Android Termux, install Python, Node.js, and C/Rust build tools (required for compiling Python security dependencies):

```bash
pkg update && pkg upgrade -y
pkg install git python nodejs clang rust binutils make -y
```

### 2. Clone Repository & Run

```bash
git clone https://github.com/ishantia/Dopile.git
cd Dopile
./start.sh
```

`start.sh` automatically creates the Python virtual environment (`.venv`), installs dependencies, runs database migrations, and launches the server.

### 3. Create Admin Account

Initialize your administrator account using the Dopile CLI:

```bash
python -m app.cli create-admin
```

Follow the prompts to set your Admin username and password.

---

## 📱 Accessing the Web Application

Once running, access Dopile from any device on your Wi-Fi network:

* **Local Machine**: `http://localhost:8080`
* **LAN Wi-Fi Devices**: `http://<YOUR_DEVICE_IP>:8080` *(e.g. `http://192.168.1.50:8080`)*

---

## ⚙️ Configuration (.env)

Customize your Dopile server by editing the `.env` file in the project root:

```ini
# Application Settings
APP_NAME=Dopile
APP_ENV=production
HOST=0.0.0.0
PORT=8080

# Security Keys (Auto-generated on init)
SECRET_KEY=your_min_32_byte_secret_key
CSRF_SECRET=your_min_32_byte_csrf_secret

# Host Restrictions
# Set to false to allow logging in from remote devices across LAN
HOST_ONLY_LOGIN=true

# Rate Limits
RATE_LIMIT_LOGIN=5/minute
RATE_LIMIT_API=100/minute
```

---

## 📜 Shell Helper Scripts

Dopile includes convenient shell scripts for process management:

* `./start.sh` — Starts database migrations and launches the Dopile server in background/foreground.
* `./stop.sh` — Gracefully stops running Dopile server processes.
* `./status.sh` — Inspects running status, network IP, and port bindings.

---

## 💻 Tech Stack

* **Backend**: FastAPI (Python 3.11+), SQLAlchemy 2.0, Pydantic v2, PyJWT, Argon2-cffi, AnyIO, Uvicorn.
* **Frontend**: React 18, TypeScript, Vite, Tailwind CSS, Lucide Icons, Workbox PWA.
* **Database**: SQLite 3 with Write-Ahead Logging (WAL) and Alembic migrations.

---

## 📄 License

Distributed under the MIT License. Created by [ishantia](https://github.com/ishantia).
