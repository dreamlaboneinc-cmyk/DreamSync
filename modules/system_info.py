
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

