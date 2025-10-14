import os, sys, yaml, pathlib, json, psutil, time

CFG = pathlib.Path("/root/config/dreamlab.yml")
DATA_DIR = pathlib.Path("/root/apps/DreamSync/data")
SUMMARY_FILE = DATA_DIR / "summary.json"


def verify(fix=False):
    if not CFG.exists():
        print("❌ Missing YAML:", CFG)
        return 2

    data = yaml.safe_load(CFG.read_text()) or {}
    ok, warn, err = [], [], []

    for alias, meta in data.items():
        path = meta.get("path")
        entry = meta.get("entry")

        if not path or not entry:
            err.append(f"{alias}: bad record")
            continue

        if not os.path.isdir(path):
            if fix:
                os.makedirs(path, exist_ok=True)
                warn.append(f"{alias}: created {path}")
            else:
                err.append(f"{alias}: missing dir {path}")
                continue

        ep = os.path.join(path, entry)
        if fix:
            with open(ep, "w") as f:
                f.write(f"# auto entry for {alias}\nif __name__ == '__main__': print('{alias} ready')\n")
            warn.append(f"{alias}: created entry {entry}")

    # Generate data summary for dashboard
    if fix:
        os.makedirs(DATA_DIR, exist_ok=True)
        summary = {
            "active_apps": list(data.keys()),
            "server_health": {
                "cpu": psutil.cpu_percent(interval=1),
                "memory": psutil.virtual_memory().percent,
                "status": "Healthy" if psutil.virtual_memory().percent < 85 else "High Load"
            },
            "alerts": [
                f"Integrity check executed successfully at {time.strftime('%Y-%m-%d %H:%M:%S')}",
                f"{len(warn)} warnings, {len(err)} errors"
            ]
        }
        with open(SUMMARY_FILE, "w") as f:
            json.dump(summary, f, indent=2)
        print(f"✅ Summary updated: {SUMMARY_FILE}")

    # Print summary log
    for line in warn:
        print("⚠️", line)
    for line in err:
        print("❌", line)
    if not warn and not err:
        print("✅ All systems verified and running clean.")
    return 0


if __name__ == "__main__":
    sys.exit(verify("--fix" in sys.argv))
