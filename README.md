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
* **👑 Complete Admin Suite**:
  * **User Management**: Create users, toggle active status, update roles, reset passwords, and delete accounts.
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
PYTHONPATH=backend .venv/bin/python -m app.cli create-admin
```

Follow the prompts to set your Admin username and password.

---

## 📱 Accessing the Web Application

Once running, access Dopile from any device on your Wi-Fi network:

* **Local Machine**: `http://localhost:8080`
* **LAN Wi-Fi Devices**: `http://<YOUR_DEVICE_IP>:8080` *(e.g. `http://192.168.1.50:8080`)*

---

## 🛠️ Admin Tools: Swagger UI API Docs & SQLite Web Interface

### 1. Interactive Swagger UI & ReDoc API Documentation
FastAPI includes built-in interactive OpenAPI documentation. By default, API docs are disabled in production mode for security. To enable them:

1. Edit `.env` and set:
   ```ini
   APP_ENV=dev
   ```
2. Restart the server (`./stop.sh && ./start.sh`).
3. Open interactive documentation in your browser:
   * **Swagger UI**: `http://<YOUR_DEVICE_IP>:8080/docs`
   * **ReDoc**: `http://<YOUR_DEVICE_IP>:8080/redoc`

### 2. Graphical SQLite Database Web Interface (`sqlite-web`)
To browse, query, and inspect raw SQLite database tables via a web browser across your LAN:

1. Install `sqlite-web` in Termux/Linux:
   ```bash
   pip install sqlite-web
   ```
2. Launch the SQLite web GUI bound to all network interfaces (`-H 0.0.0.0`):
   ```bash
   sqlite_web ./data/dopile.db -H 0.0.0.0 -p 8081
   ```
3. Open in any browser on your Wi-Fi network: `http://<YOUR_DEVICE_IP>:8081`

---

## 🔋 Making Dopile Unkillable & Auto-Starting on Android Boot

If you are hosting Dopile on an Android phone via Termux and want the server to **never get killed by Android** and **automatically start whenever your phone reboots or powers on**, follow these steps:

### Step 1: Prevent Android from Killing Termux (Disable Battery Optimization)
1. On your phone, go to **Android Settings $\rightarrow$ Apps $\rightarrow$ Termux $\rightarrow$ Battery**.
2. Set Battery Usage to **Unrestricted** (or "Don't optimize").
3. Dopile's `./start.sh` script automatically requests a CPU Wake Lock via `termux-wake-lock` when launching to keep the CPU active.

### Step 2: Auto-Start Dopile on Phone Boot (Termux:Boot Setup)
1. Install the **Termux:Boot** app (available on F-Droid or GitHub).
2. Launch the **Termux:Boot** app once on your phone so Android registers the boot permission.
3. In Termux, run this one-line setup command to create the boot script:

```bash
mkdir -p ~/.termux/boot
cat << 'EOF' > ~/.termux/boot/start-dopile.sh
#!/data/data/com.termux/files/usr/bin/sh
termux-wake-lock
cd ~/Dopile && ./start.sh
EOF
chmod +x ~/.termux/boot/start-dopile.sh
```

> **Note**: You do **not** need to manually activate `.venv` in the boot script because `./start.sh` automatically detects, activates, and handles `.venv` for you!

Now, whenever your Android phone powers on or reboots, **Dopile will automatically start up in the background and remain active 24/7**!

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
