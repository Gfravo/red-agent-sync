"""Acumula eventos nuevos en data/cache/events.json sin duplicar ni perder los anteriores.

Uso (Claude lo invoca como módulo tras buscar eventos nuevos vía WebSearch):
    from scripts.import_events import import_events
    import_events([
        {"title": "...", "date": "...", "location": "...", "link": "...", "why": "...", "tags": [...]},
        ...
    ])
"""
import json
import re
from datetime import date
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
EVENTS_PATH = ROOT / "data" / "cache" / "events.json"


def slugify(text):
    return re.sub(r"[^a-z0-9]+", "-", text.lower()).strip("-")


def load_events_data():
    if EVENTS_PATH.exists():
        return json.loads(EVENTS_PATH.read_text(encoding="utf-8"))
    return {"generated_on": None, "events": []}


def save_events_data(data):
    EVENTS_PATH.parent.mkdir(parents=True, exist_ok=True)
    EVENTS_PATH.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")


def import_events(new_events):
    """new_events: lista de dicts con title/date/location/link/why/tags.
    Dedup por (title + location) normalizados. Devuelve cuántos se añadieron."""
    data = load_events_data()
    existing_keys = {
        (e["title"].strip().lower(), e.get("location", "").strip().lower()) for e in data["events"]
    }

    added = 0
    for ev in new_events:
        key = (ev["title"].strip().lower(), ev.get("location", "").strip().lower())
        if key in existing_keys:
            continue
        ev = dict(ev)
        ev.setdefault("id", slugify(ev["title"]))
        ev.setdefault("found_on", date.today().isoformat())
        data["events"].append(ev)
        existing_keys.add(key)
        added += 1

    data["generated_on"] = date.today().isoformat()
    save_events_data(data)
    return added
