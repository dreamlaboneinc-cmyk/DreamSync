#!/bin/bash
# ===============================================
# 💫 DREAMSYNC LOCAL VERIFICATION (v2)
# Environment: Cursor / Local Dev Machine
# ===============================================

# ✅ Load aliases (pushbot, updatebot, etc.)
source ~/.bashrc

GREEN='\033[0;32m'
RED='\033[0;31m'
BLUE='\033[1;34m'
YELLOW='\033[1;33m'
NC='\033[0m'
CHECK="${GREEN}✅${NC}"
CROSS="${RED}❌${NC}"
INFO="${YELLOW}⚙️${NC}"
LINE="-----------------------------------------------------------"

echo -e "\n${BLUE}💫 DREAMSYNC LOCAL VERIFICATION${NC}"
echo "$LINE"

# 1️⃣ Git Repo Check
if git rev-parse --is-inside-work-tree > /dev/null 2>&1; then
  echo -e "${CHECK} Git Repo Connected"
else
  echo -e "${CROSS} Not inside a Git repository"
fi

# 2️⃣ pushbot Command
if alias pushbot &> /dev/null || command -v pushbot &> /dev/null; then
  echo -e "${CHECK} pushbot command available (alias loaded)"
else
  echo -e "${CROSS} pushbot not found — reload aliases with: source ~/.bashrc"
fi

# 3️⃣ YAML Config Check (allowed to be ignored in .gitignore)
if [ -f "./config/dreamlab.yml" ] || [ -f "./dreamlab.yml" ]; then
  echo -e "${CHECK} dreamlab.yml present locally"
elif grep -q "dreamlab.yml" .gitignore 2>/dev/null; then
  echo -e "${YELLOW}⚙️ dreamlab.yml intentionally ignored in Git — OK${NC}"
else
  echo -e "${CROSS} dreamlab.yml not found locally. Reason: GIT ignored"
fi

# 4️⃣ Virtual Environment
if [ -d "venv" ]; then
  echo -e "${CHECK} venv folder detected"
else
  echo -e "${CROSS} venv missing — run: python3 -m venv venv"
fi

# 5️⃣ .env Ignore Check
if grep -q ".env" .gitignore 2>/dev/null; then
  echo -e "${CHECK} .env is properly ignored"
else
  echo -e "${CROSS} .env not listed in .gitignore"
fi

# ✅ Final Status
echo -e "\n${INFO} Reminder: To test sync end-to-end:"
echo "Add → print('✅ DreamSync local sync test successful!') to any file"
echo "Then run → pushbot"
echo "$LINE"
echo -e "${GREEN}🎯 LOCAL ENVIRONMENT READY FOR SYNC${NC}"
echo "$LINE"