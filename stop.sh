#!/usr/bin/env bash
# Dopile - Stop script
echo "[*] Stopping Dopile server..."

# Kill uvicorn processes
pkill -f "uvicorn app.main:app" 2>/dev/null || sudo pkill -f "uvicorn app.main:app" 2>/dev/null || true

# Kill any process holding port 8080
if command -v fuser >/dev/null 2>&1; then
    fuser -k 8080/tcp 2>/dev/null || sudo fuser -k 8080/tcp 2>/dev/null || true
fi

echo "[+] Done."
