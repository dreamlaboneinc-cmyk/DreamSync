#!/bin/bash
# ===============================================
# 🧹 DREAMSYNC UVICORN CLEANUP + SERVICE RESET
# Author: Dream Lab One Inc.
# ===============================================

APP_DIR="/root/apps/DreamSync"
SERVICE_FILE="/etc/systemd/system/DreamSync.service"
LOG_FILE="/root/logs/dreamsync.log"

echo "-------------------------------------------------------"
echo "🧠 Cleaning up old Uvicorn traces and resetting DreamSync"
echo "-------------------------------------------------------"

# Step 1: Locate any uvicorn traces
echo "🔍 Scanning for 'uvicorn' references..."
grep -r "uvicorn" "$APP_DIR" --color=always || echo "✅ No uvicorn references found in app code."

# Step 2: Remove uvicorn from requirements.txt if found
REQ_FILE="$APP_DIR/requirements.txt"
if grep -q "uvicorn" "$REQ_FILE" 2>/dev/null; then
    echo "🧹 Removing uvicorn from requirements.txt..."
    sed -i '/uvicorn/d' "$REQ_FILE"
else
    echo "✅ No uvicorn entry in requirements.txt"
fi

# Step 3: Clean installer.sh if it references uvicorn
INSTALLER_FILE="$APP_DIR/installer.sh"
if grep -q "uvicorn" "$INSTALLER_FILE" 2>/dev/null; then
    echo "🧼 Cleaning installer.sh..."
    sed -i 's/uvicorn.*/python core.py/g' "$INSTALLER_FILE"
else
    echo "✅ No uvicorn reference in installer.sh"
fi

# Step 4: Uninstall uvicorn from virtual environment
echo "🚮 Uninstalling uvicorn from venv (if present)..."
source "$APP_DIR/venv/bin/activate"
pip uninstall -y uvicorn >/dev/null 2>&1 && echo "✅ uvicorn removed from venv." || echo "✅ uvicorn not installed."

# Step 5: Rebuild clean systemd service
echo "🛠️  Rebuilding DreamSync systemd service..."
sudo systemctl stop DreamSync.service 2>/dev/null
sudo systemctl disable DreamSync.service 2>/dev/null
sudo rm -f "$SERVICE_FILE"

cat <<EOF | sudo tee "$SERVICE_FILE" >/dev/null
[Unit]
Description=DreamSync – Core Service
After=network.target

[Service]
User=root
WorkingDirectory=$APP_DIR
ExecStart=$APP_DIR/venv/bin/python core.py
Restart=always
RestartSec=5
Environment="PYTHONUNBUFFERED=1"
StandardOutput=append:$LOG_FILE
StandardError=append:$LOG_FILE

[Install]
WantedBy=multi-user.target
EOF

# Step 6: Prepare log directory
echo "🗂️  Ensuring log directory exists..."
sudo mkdir -p /root/logs
sudo touch "$LOG_FILE"

# Step 7: Reload and start service
echo "🚀 Restarting DreamSync service..."
sudo systemctl daemon-reload
sudo systemctl enable DreamSync.service
sudo systemctl restart DreamSync.service

# Step 8: Verify
sleep 2
if systemctl is-active --quiet DreamSync.service; then
    echo "✅ DreamSync Service is Active and Running"
else
    echo "❌ DreamSync Service failed to start — check logs below:"
fi

echo "-------------------------------------------------------"
echo "📜 Recent log output:"
tail -n 10 "$LOG_FILE"
echo "-------------------------------------------------------"
echo "🎯 Cleanup complete."