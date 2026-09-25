
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
        for a,m in data.items(): print(f"[{a}] {active(a,m.get(systemd,False))}")
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

