from __future__ import annotations
from pathlib import Path
import httpx

class DreamAPIError(RuntimeError): pass

class DreamAPIClient:
    def __init__(self, base_url="http://127.0.0.1:8275", timeout=60.0, key_path="/etc/dream-api/secrets/client.key"):
        self.base_url=base_url.rstrip("/")
        self.timeout=timeout
        self.key_path=Path(key_path)
    def _headers(self) -> dict:
        if not self.key_path.exists():
            raise DreamAPIError("Dream API client credential is unavailable")
        token=self.key_path.read_text().strip()
        if not token:
            raise DreamAPIError("Dream API client credential is empty")
        return {"Authorization":f"Bearer {token}"}
    def health(self) -> dict:
        r=httpx.get(f"{self.base_url}/health",timeout=10.0)
        r.raise_for_status(); data=r.json()
        if data.get("billing_mode")!="FREE_ONLY" or not data.get("ok"):
            raise DreamAPIError("Dream API is not healthy in FREE_ONLY mode")
        return data
    def complete(self,prompt: str,model="dream-auto") -> str:
        self.health()
        body={"model":model,"messages":[{"role":"user","content":prompt}],"stream":False}
        r=httpx.post(f"{self.base_url}/v1/chat/completions",json=body,headers=self._headers(),timeout=self.timeout)
        r.raise_for_status(); data=r.json()
        return data["choices"][0]["message"]["content"]
