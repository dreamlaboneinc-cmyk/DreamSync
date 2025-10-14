
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

