"""Reusable template library: JSON per category in data/library/."""
import json, os
from datetime import datetime
import config
def _dir(): d=os.path.join(config.DATA_DIR,"library"); os.makedirs(d, exist_ok=True); return d
def _file(cat): return os.path.join(_dir(), f"{cat}.json")
def _load(cat):
    p=_file(cat)
    if not os.path.exists(p): return []
    with open(p,encoding="utf-8") as f: return json.load(f)
def _save(cat, items):
    with open(_file(cat),"w",encoding="utf-8") as f: json.dump(items,f,indent=2)
def add_item(category, title, text, tags=None):
    if category not in config.LIBRARY_CATEGORIES: raise ValueError(f"Unknown category {category}. Allowed: {config.LIBRARY_CATEGORIES}")
    items=_load(category); nid=str(max([int(i['id']) for i in items], default=0)+1)
    item={"id":nid,"title":title,"text":text,"tags":tags or [],"created_at":datetime.now().isoformat()}
    items.append(item); _save(category,items); return item
def list_items(category=None):
    if category: return _load(category)
    out={}
    for c in config.LIBRARY_CATEGORIES: out[c]=_load(c)
    return out
def get_item(category, item_id):
    for i in _load(category):
        if str(i["id"])==str(item_id): return i
    return None
def delete_item(category, item_id):
    items=_load(category); new=[i for i in items if str(i["id"])!=str(item_id)]
    _save(category,new); return len(new)!=len(items)
