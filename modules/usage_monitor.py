
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

