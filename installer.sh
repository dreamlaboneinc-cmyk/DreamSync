#!/usr/bin/env bash
# DreamSync Core X v3 — One-Shot Installer (Resilient / No-Halt)
# Run as: sudo bash /root/apps/DreamSync/installer.sh

# --------- config & paths ----------
APPS="/root/apps"
DS="${APPS}/DreamSync"
CFG_DIR="/root/config"
YAML="${CFG_DIR}/dreamlab.yml"
LOG_DIR="/var/log/dreamsync"
BACKUPS="/root/backups"
ENV_FILE="${DS}/.env"
INSTALL_LOG="${LOG_DIR}/install.log"

# --------- helpers (resilient run + logging) ----------
mkdir -p "$APPS" "$DS" "$CFG_DIR" "$LOG_DIR" "$BACKUPS"
touch "$INSTALL_LOG"

log(){ echo -e "$@" | tee -a "$INSTALL_LOG" ; }
run(){
  # usage: run <cmd> [args...]
  "$@" >>"$INSTALL_LOG" 2>&1
  RC=$?
  if [ $RC -ne 0 ]; then
    echo "⚠️  FAILED: $*  (rc=$RC). Continuing. See $INSTALL_LOG" | tee -a "$INSTALL_LOG"
  fi
  return 0
}

# ----- .env bootstrap (idempotent) -----
if [[ ! -f "$ENV_FILE" ]]; then
  cat >"$ENV_FILE" <<'ENV'
OPENAI_API_KEY=sk-yourkeyhere
LINODE_IP=xxx.xxx.xxx.xxx
OPENAI_CREDITS_PREPAID_USD=100
TELEGRAM_BOT_TOKEN=
TELEGRAM_CHAT_ID=
ENV
  chmod 600 "$ENV_FILE"
  log "🧩 Created .env bootstrap."
fi

# ----- Core packages (best-effort; no apt-get update lock blockers) -----
log "📦 Installing core packages (best-effort)…"
run dpkg --configure -a
run apt-get update -y
run apt-get install -y python3 python3-pip git jq zip unzip curl cron

# ----- Python deps (best-effort) -----
log "⚙️  Installing Python deps…"
run python3 -m pip install -U pip
run python3 -m pip install -U fastapi "python core.py

# ----- Registry (alias → entry/systemd/fullname) -----
declare -A ENTRY SYS FULL
ENTRY[CommandOne]="main.py";          SYS[CommandOne]=true;  FULL[CommandOne]="Command One – Live System Intel"
ENTRY[DreamSync]="core.py";           SYS[DreamSync]=true;   FULL[DreamSync]="DreamSync – Agentic Coding & Deployment"
ENTRY[DreamFunnel]="server.py";       SYS[DreamFunnel]=true; FULL[DreamFunnel]="Dream Funnel System – Automated Conscious Commerce"
ENTRY[DreamTube]="app.py";            SYS[DreamTube]=true;   FULL[DreamTube]="DreamTube Studio – Create · Channel · Broadcast"
ENTRY[Impact]="main.py";              SYS[Impact]=false;     FULL[Impact]="Impact – Relief Initiative"
ENTRY[TheOracle]="oracle.py";         SYS[TheOracle]=false;  FULL[TheOracle]="The Oracle – Wisdom Through Code"
ENTRY[AudiobookCreator]="run.py";     SYS[AudiobookCreator]=false; FULL[AudiobookCreator]="Audiobook Creator+ – Voices of Light"
ENTRY[Dwella]="start.py";             SYS[Dwella]=false;     FULL[Dwella]="Dwella – Renting Reimagined"
ENTRY[QuantumTradeAI]="bot.py";       SYS[QuantumTradeAI]=true; FULL[QuantumTradeAI]="QuantumTrade AI – Intelligent Wealth"
ENTRY[DreamPortal]="index.py";        SYS[DreamPortal]=true; FULL[DreamPortal]="Dream Portal – Unified Ecosystem for Awareness & Commerce"
ENTRY[SolarAscend]="app.py";          SYS[SolarAscend]=true; FULL[SolarAscend]="My Solar Ascend Platform"

write_file () { local t="$1"; shift; local tmp; tmp="$(mktemp)"; cat >"$tmp" <<<"$*"; mkdir -p "$(dirname "$t")"; if [[ ! -f "$t" ]] || ! cmp -s "$tmp" "$t"; then mv "$tmp" "$t"; else rm -f "$tmp"; fi; }
ensure_app () { local a="$1"; local e="$2"; local d="${APPS}/${a}"; mkdir -p "$d"; if [[ ! -f "${d}/${e}" ]]; then cat > "${d}/${e}" <<EOP
# Entry point for ${a}
if __name__ == "__main__":
    print("${a} ready")
EOP
fi; }
yaml_append_if_missing () {
  local a="$1" e="$2" s="$3" f="$4" p="${APPS}/${a}"
  [[ -f "$YAML" ]] || echo "# Dream Lab One registry" >"$YAML"
  if ! grep -qE "^${a}:" "$YAML"; then
    cat >>"$YAML" <<EOP
${a}:
  full_name: "${f}"
  alias: "${a}"
  path: "${p}"
  entry: "${e}"
  systemd: ${s}
EOP
  fi
}

# ----- Create app dirs + YAML -----
for a in "${!ENTRY[@]}"; do
  ensure_app "$a" "${ENTRY[$a]}"
  yaml_append_if_missing "$a" "${ENTRY[$a]}" "${SYS[$a]}" "${FULL[$a]}"
done

# ----- DreamSync modules -----
write_file "${DS}/config_reader.py" '
import os, yaml
def load_config():
    p="/root/config/dreamlab.yml"
    if not os.path.exists(p):
        p=os.path.expanduser("~/DreamLab/config/dreamlab.yml")
    try:
        with open(p,"r") as f: return yaml.safe_load(f) or {}
    except Exception as e:
        print(f"⚠️ config read error: {e}"); return {}
'

write_file "${DS}/integrity_check.py" '
import os, sys, yaml, pathlib
CFG=pathlib.Path("/root/config/dreamlab.yml")
def verify(fix=False):
    if not CFG.exists():
        print("❌ Missing YAML:", CFG); return 2
    data=yaml.safe_load(CFG.read_text()) or {}
    ok,warn,err=[],[],[]
    for alias,meta in data.items():
        path=meta.get("path"); entry=meta.get("entry")
        if not path or not entry: err.append(f"{alias}: bad record"); continue
        if not os.path.isdir(path):
            if fix: os.makedirs(path,exist_ok=True); warn.append(f"{alias}: created {path}")
            else: err.append(f"{alias}: missing dir {path}"); continue
        ep=os.path.join(path,entry)
        if not os.path.isfile(ep):
            if fix:
                open(ep,"w").write(f"# auto entry for {alias}\\nif __name__==\\"__main__\\": print(\\"{alias} ready\\")\\n")
                warn.append(f"{alias}: created entry {entry}")
            else:
                err.append(f"{alias}: missing entry {entry}"); continue
        ok.append(alias)
    if ok: print("OK:", ", ".join(ok))
    if warn: print("WARN:"); [print(" -",x) for x in warn]
    if err: print("ERR:"); [print(" -",x) for x in err]
    return 0 if not err else 2
if __name__=="__main__": sys.exit(verify("--fix" in sys.argv))
'

write_file "${DS}/deploy.py" '
import os, sys, subprocess, yaml, pathlib
CFG=pathlib.Path("/root/config/dreamlab.yml")
LOG="/var/log/dreamsync/bridge_activity.log"
def sh(cmd,cwd=None): return subprocess.run(cmd,cwd=cwd,shell=True,capture_output=True,text=True)
def load(): return yaml.safe_load(CFG.read_text()) if CFG.exists() else {}
def pull(path):
    if not (path and os.path.isdir(path)): return "skip: missing path"
    if not os.path.isdir(os.path.join(path,".git")): return "skip: not a git repo"
    r=sh("git pull --ff-only",cwd=path); return r.stdout.strip() or r.stderr.strip()
def restart(alias,meta):
    entry=meta.get("entry"); path=meta.get("path"); sysd=meta.get("systemd",False)
    if sysd: subprocess.run(["systemctl","restart",f"{alias}.service"],check=False); return f"systemd restarted {alias}"
    entry_path=os.path.join(path,entry)
    subprocess.run(["pkill","-f",entry_path],check=False)
    subprocess.Popen(["nohup","python3",entry_path],cwd=path,stdout=subprocess.DEVNULL,stderr=subprocess.DEVNULL)
    return f"spawned {alias}"
def do_one(alias,data):
    meta=data.get(alias) or {}; out=pull(meta.get("path")); act=restart(alias,meta)
    with open(LOG,"a") as f: f.write(f"{alias}: {out} | {act}\\n")
    print(f"{alias}: {out} | {act}")
def main():
    data=load() or {}
    if len(sys.argv)<2: print("usage: updatebot <AppName|all>"); sys.exit(1)
    target=sys.argv[1]
    if target=="all": [do_one(a,data) for a in data.keys()]
    else:
        if target not in data: print("unknown app"); sys.exit(2)
        do_one(target,data)
if __name__=="__main__": main()
'

write_file "${DS}/bridge.py" '
import os, sys, subprocess, yaml, pathlib
CFG=pathlib.Path("/root/config/dreamlab.yml")
def load(): return yaml.safe_load(CFG.read_text()) if CFG.exists() else {}
def active(alias,sysd):
    if sysd:
        import subprocess as sp
        r=sp.run(["systemctl","is-active",f"{alias}.service"],capture_output=True,text=True)
        return r.stdout.strip()
    return "manual"
def main():
    if len(sys.argv)==1 or sys.argv[1]=="status":
        data=load() or {}
        for a,m in data.items(): print(f"[{a}] {active(a,m.get('systemd',False))}")
        return
    if sys.argv[1]=="restart" and len(sys.argv)>2:
        a=sys.argv[2]; d=load() or {}; m=d.get(a)
        if not m: print("unknown app"); return
        if m.get("systemd",False): __import__("subprocess").run(["systemctl","restart",f"{a}.service"])
        else:
            p=m.get("path"); e=m.get("entry")
            __import__("subprocess").run(["pkill","-f",os.path.join(p,e)],check=False)
            __import__("subprocess").Popen(["nohup","python3",e],cwd=p)
        print("ok"); return
    print("usage: bridge [status|restart <AppName>]")
if __name__=="__main__": main()
'

# ----- Modules: usage monitor + system info + dashboard -----
mkdir -p "${DS}/modules" "${DS}/dashboard/templates" "${DS}/dashboard/static"

write_file "${DS}/modules/usage_monitor.py" '
import os, json, datetime, requests, pathlib
from dotenv import load_dotenv
load_dotenv("/root/apps/DreamSync/.env")
OPENAI_API_KEY=os.getenv("OPENAI_API_KEY","")
CREDITS=float(os.getenv("OPENAI_CREDITS_PREPAID_USD","0") or 0)
LOG_DIR=pathlib.Path("/var/log/dreamsync"); LOG_DIR.mkdir(parents=True, exist_ok=True)
USAGE_LOG=LOG_DIR/"usage_log.json"; ALERTS_LOG=LOG_DIR/"alerts.log"
THRESH=0.80
def alert(msg):
    ts=datetime.datetime.utcnow().isoformat()+"Z"
    with open(ALERTS_LOG,"a") as f: f.write(f"{ts} | {msg}\\n")
    tok=os.getenv("TELEGRAM_BOT_TOKEN"); chat=os.getenv("TELEGRAM_CHAT_ID")
    if tok and chat:
        try: requests.post(f"https://api.telegram.org/bot{tok}/sendMessage",json={"chat_id":chat,"text":msg},timeout=10)
        except Exception: pass
def record(total,pct):
    hist=[]
    if USAGE_LOG.exists():
        try: hist=json.loads(USAGE_LOG.read_text() or "[]")
        except Exception: hist=[]
    hist.append({"timestamp":datetime.datetime.utcnow().isoformat()+"Z","total_spend_usd":round(total,4),"credits_usd":CREDITS,"percent_used":round(pct*100,2)})
    USAGE_LOG.write_text(json.dumps(hist,indent=2))
def fetch():
    if not OPENAI_API_KEY: alert("⚠️ OPENAI_API_KEY missing; usage check skipped."); return 0.0
    try:
        today=datetime.date.today(); start=today.replace(day=1).isoformat(); end=today.isoformat()
        r=requests.get(f"https://api.openai.com/v1/usage?start_date={start}&end_date={end}",headers={"Authorization":f"Bearer {OPENAI_API_KEY}"},timeout=15)
        if r.status_code!=200: alert(f"⚠️ OpenAI usage HTTP {r.status_code}"); return 0.0
        return float(r.json().get("total_usage_usd",0.0))
    except Exception as e:
        alert(f"⚠️ Usage fetch error: {e}"); return 0.0
def main():
    spent=fetch(); pct=(spent/CREDITS) if CREDITS>0 else 0.0
    record(spent,pct)
    if CREDITS>0 and pct>=THRESH: alert(f"‼️ OpenAI usage {spent:.2f} USD — {pct*100:.1f}% of {CREDITS:.2f}")
if __name__=="__main__": main()
'

write_file "${DS}/modules/system_info.py" '
import os, json, time, psutil, pathlib
LOG=pathlib.Path("/var/log/dreamsync")
def alerts(n=25):
    p=LOG/"alerts.log"
    return (p.read_text(errors="ignore").splitlines()[-n:][::-1]) if p.exists() else []
def usage():
    p=LOG/"usage_log.json"
    if not p.exists(): return {"total_spend_usd":0,"percent_used":0,"credits_usd":0}
    try:
        arr=json.loads(p.read_text() or "[]"); return arr[-1] if arr else {"total_spend_usd":0,"percent_used":0,"credits_usd":0}
    except Exception: return {"total_spend_usd":0,"percent_used":0,"credits_usd":0}
def metrics():
    return {"uptime_sec": int(time.time()-psutil.boot_time()), "cpu_percent": psutil.cpu_percent(interval=0.2), "mem": psutil.virtual_memory()._asdict(), "loadavg": os.getloadavg() if hasattr(os,"getloadavg") else (0,0,0)}
'

write_file "${DS}/dashboard/main.py" '
import pathlib, yaml
from fastapi import FastAPI
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from jinja2 import Environment, FileSystemLoader
from modules.system_info import metrics, usage, alerts
BASE=pathlib.Path("/root/apps/DreamSync")
CONFIG=pathlib.Path("/root/config/dreamlab.yml")
app=FastAPI(title="DreamSync Dashboard")
app.mount("/static", StaticFiles(directory=str(BASE/"dashboard"/"static")), name="static")
env=Environment(loader=FileSystemLoader(str(BASE/"dashboard"/"templates")))
def load_apps():
    if CONFIG.exists():
        data=yaml.safe_load(CONFIG.read_text()) or {}
        return [{"alias":k, **(v or {})} for k,v in data.items()]
    return []
@app.get("/api/dashboard")
def api(): return {"usage": usage(), "metrics": metrics(), "apps": load_apps(), "alerts": alerts()}
@app.get("/", response_class=HTMLResponse)
def root():
    tmpl=env.get_template("index.html"); return tmpl.render()
'

write_file "${DS}/dashboard/templates/index.html" '<!doctype html>
<html><head><meta charset="utf-8"/><title>DreamSync Dashboard</title>
<script src="/static/dashboard.js" defer></script><script src="https://cdn.tailwindcss.com"></script>
</head><body class="bg-slate-950 text-slate-100"><div class="max-w-6xl mx-auto p-6">
<h1 class="text-3xl font-bold mb-4">DreamSync Dashboard</h1>
<div id="usage" class="mb-6 p-4 rounded bg-slate-900 border border-slate-800"></div>
<div class="grid grid-cols-1 md:grid-cols-2 gap-6">
  <div class="p-4 rounded bg-slate-900 border border-slate-800"><h2 class="font-semibold mb-2">Active Apps</h2><ul id="apps" class="space-y-1 text-sm"></ul></div>
  <div class="p-4 rounded bg-slate-900 border border-slate-800"><h2 class="font-semibold mb-2">Server Health</h2><pre id="health" class="text-xs whitespace-pre-wrap"></pre></div>
</div>
<div class="mt-6 p-4 rounded bg-slate-900 border border-slate-800"><h2 class="font-semibold mb-2">Recent Alerts</h2><pre id="alerts" class="text-xs whitespace-pre-wrap"></pre></div>
<p class="text-xs mt-6 opacity-70">Auto-refreshes every 10s.</p></div></body></html>'

write_file "${DS}/dashboard/static/dashboard.js" '
async function refresh(){
  const r=await fetch("/api/dashboard",{cache:"no-store"}); const d=await r.json();
  const u=d.usage||{}; const credits=+u.credits_usd||0, spent=+u.total_spend_usd||0, pct=(+u.percent_used||0)/100.0;
  const bar=pct>=0.8?"bg-red-600":"bg-emerald-600";
  document.getElementById("usage").innerHTML=`<div class="flex items-center justify-between mb-2">
    <div>OpenAI Spend: <span class="font-semibold">$${spent.toFixed(2)}</span> of $${credits.toFixed(2)}</div>
    <div class="text-sm opacity-80">${(pct*100).toFixed(1)}% used</div></div>
    <div class="w-full h-3 bg-slate-800 rounded"><div class="h-3 ${bar} rounded" style="width:${Math.min(100,pct*100)}%"></div></div>`;
  const apps=d.apps||[]; document.getElementById("apps").innerHTML=apps.length?apps.map(a=>`<li class="flex justify-between"><span>${a.alias}</span><span class="opacity-70 text-xs">${a.entry||""}</span></li>`).join(""):"<li class='opacity-70'>No apps</li>";
  const m=d.metrics||{}, up=m.uptime_sec||0; document.getElementById("health").textContent=`Uptime: ${Math.floor(up/3600)}h\nCPU: ${m.cpu_percent||0}%\nLoad: ${(m.loadavg||[]).join(", ")}\nMem: ${m.mem?((m.mem.used/1e9).toFixed(2)+' / '+(m.mem.total/1e9).toFixed(2)+' GB'):'n/a'}`;
  document.getElementById("alerts").textContent=(d.alerts||[]).join("\n")||"No recent alerts.";
}
refresh(); setInterval(refresh,10000);
'

# ----- Aliases + updatebot shim -----
grep -q "pushbot" /root/.bash_aliases 2>/dev/null || cat >>/root/.bash_aliases <<'ALIAS'
alias pushbot='git add -A && git commit -m "AI patch" && git push origin main'
alias botlog='git log -1 --stat'
alias checksync='python3 /root/apps/DreamSync/integrity_check.py'
alias bridge='python3 /root/apps/DreamSync/bridge.py'
ALIAS

echo '#!/usr/bin/env bash' > /usr/local/bin/updatebot
echo 'exec python3 /root/apps/DreamSync/deploy.py "$@"' >> /usr/local/bin/updatebot
chmod +x /usr/local/bin/updatebot

# ----- systemd units for systemd=true apps -----
for a in "${!ENTRY[@]}"; do
  if [[ "${SYS[$a]}" == "true" ]]; then
    unit="/etc/systemd/system/${a}.service"
    path="${APPS}/${a}"
    entry="${ENTRY[$a]}"
    cat >"$unit" <<EUS
[Unit]
Description=${a} Service
After=network.target
[Service]
WorkingDirectory=${path}
ExecStart=/usr/bin/python3 ${entry}
Restart=on-failure
User=root
Environment=PYTHONUNBUFFERED=1
[Install]
WantedBy=multi-user.target
EUS
    run systemctl daemon-reload
    [[ -s "${path}/${entry}" ]] && run systemctl enable "${a}.service"
    [[ -s "${path}/${entry}" ]] && run systemctl restart "${a}.service"
  fi
done

# ----- Dashboard service (FastAPI on :5050) -----
cat >/etc/systemd/system/DreamSyncDashboard.service <<EUS
[Unit]
Description=DreamSync Dashboard (FastAPI)
After=network.target
[Service]
WorkingDirectory=${DS}
ExecStart=/usr/bin/python3 -m python core.py
Restart=always
User=root
Environment=PYTHONUNBUFFERED=1
[Install]
WantedBy=multi-user.target
EUS
run systemctl daemon-reload
run systemctl enable DreamSyncDashboard
run systemctl restart DreamSyncDashboard

# ----- Cron (usage monitor every 6h) -----
echo "0 */6 * * * root /usr/bin/python3 /root/apps/DreamSync/modules/usage_monitor.py >> /var/log/dreamsync/usage_monitor.cron.log 2>&1" > /etc/cron.d/dreamsync_usage
chmod 644 /etc/cron.d/dreamsync_usage
run systemctl restart cron || run service cron restart

# ----- Final integrity pass -----
run python3 "${DS}/integrity_check.py" --fix

# ----- Summary -----
cat > "${LOG_DIR}/install_summary.log" <<EOS
✅ /root/config/dreamlab.yml created/updated
✅ All app directories present with correct entry names
✅ DreamSync core + deploy + bridge installed
✅ Dashboard running on port 5050
✅ Cron installed for usage monitoring (6h)
✅ Systemd services written for systemd-enabled apps
✅ Aliases ready: pushbot, updatebot, botlog, checksync, bridge
EOS

echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "✨ DREAMSYNC CORE X v3 – INSTALL COMPLETE ✨"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
cat "${LOG_DIR}/install_summary.log"
echo "Dashboard: http://${LINODE_IP:-<YOUR_IP>}:5050/"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "💫 Dream Lab One — \"Imagine What’s Possible.\""
