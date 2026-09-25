
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

