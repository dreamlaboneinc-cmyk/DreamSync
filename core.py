"""DreamSync V2 core service: conservative coordinator heartbeat."""
import json, signal, time
from pathlib import Path
from dreamsync.config import load_project
from dreamsync.dream_api import DreamAPIClient

RUN=True
def stop(*_):
    global RUN; RUN=False

def main():
    signal.signal(signal.SIGTERM,stop); signal.signal(signal.SIGINT,stop)
    cfg=load_project(Path(__file__).resolve().parent)
    print(json.dumps({"service":"DreamSync","version":"2.0.0-alpha.1","mode":cfg.raw.get("mode"),"ai":"dream-api/FREE_ONLY"}),flush=True)
    while RUN:
        try: DreamAPIClient(cfg.ai.get("base_url")).health()
        except Exception as e: print(f"Dream API health warning: {type(e).__name__}",flush=True)
        for _ in range(30):
            if not RUN: break
            time.sleep(1)
if __name__=="__main__": main()
