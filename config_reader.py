
import os, yaml
def load_config():
    p="/root/config/dreamlab.yml"
    if not os.path.exists(p):
        p=os.path.expanduser("~/DreamLab/config/dreamlab.yml")
    try:
        with open(p,"r") as f: return yaml.safe_load(f) or {}
    except Exception as e:
        print(f"⚠️ config read error: {e}"); return {}

