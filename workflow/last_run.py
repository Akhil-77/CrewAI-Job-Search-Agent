import json, os
import config
def _path(): os.makedirs(config.DATA_DIR, exist_ok=True); return os.path.join(config.DATA_DIR,"last_run.json")
def write_last_run(data):
    with open(_path(),"w",encoding="utf-8") as f: json.dump(data,f,indent=2)
def read_last_run():
    p=_path()
    if not os.path.exists(p): return None
    with open(p,encoding="utf-8") as f: return json.load(f)
