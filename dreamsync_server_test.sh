#!/bin/bash
# ===============================================
# 🌐 DREAMSYNC SERVER VERIFICATION
# Environment: Linode / Remote Server
# ===============================================
GREEN='\033[0;32m'
RED='\033[0;31m'
BLUE='\033[1;34m'
YELLOW='\033[1;33m'
NC='\033[0m'
CHECK="${GREEN}✅${NC}"
CROSS="${RED}❌${NC}"
INFO="${YELLOW}⚙️${NC}"
LINE="-----------------------------------------------------------"

echo -e "\n${BLUE}🌐 DREAMSYNC SERVER VERIFICATION${NC}"
echo "$LINE"

# 🔁 Restart Service Before Checking
echo -e "${INFO} Restarting DreamSync Service..."
systemctl daemon-reload >/dev/null 2>&1
systemctl restart DreamSync.service
sleep 2

# 1️⃣ Service Check
if systemctl is-active --quiet DreamSync.service; then
  echo -e "${CHECK} DreamSync Service is Active and Running"
else
  echo -e "${CROSS} DreamSync Service Inactive — check logs with: journalctl -u DreamSync.service -n 20"
fi

# 2️⃣ API Health Check (Localhost)
if curl -s http://127.0.0.1:5050/api/dashboard | grep -q "usage"; then
  echo -e "${CHECK} FastAPI Responding (Localhost)"
else
  echo -e "${CROSS} FastAPI Not Responding — check app.py"
fi

# 3️⃣ Public Dashboard Check
if curl -s http://172.105.159.96:5050 | grep -q "html"; then
  echo -e "${CHECK} Public Dashboard Accessible"
else
  echo -e "${CROSS} Public Dashboard Unreachable"
fi

# 4️⃣ Repo Integrity Check
cd /root/apps/DreamSync || exit
if git rev-parse --is-inside-work-tree > /dev/null 2>&1; then
  REMOTE_URL=$(git config --get remote.origin.url)
  echo -e "${CHECK} GitHub Repo Linked → ${REMOTE_URL}"
else
  echo -e "${CROSS} Git Repo Missing or Not Initialized"
fi

# 5️⃣ venv Activation Check
if [ -d "venv" ]; then
  echo -e "${CHECK} venv Found and Ready"
else
  echo -e "${CROSS} venv Missing in /root/apps/DreamSync"
fi

echo "$LINE"
echo -e "${GREEN}🚀 SERVER VERIFIED: DreamSync Online & Serving${NC}"
echo "$LINE"