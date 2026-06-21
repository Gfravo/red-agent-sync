"""Importa ofertas de empleo (ya extraídas de las alertas de Gmail por Claude vía el
conector de Gmail) en data/cache/job_postings.json, puntuando y sin duplicar.

Uso (desde Python, no hay CLI interactiva — Claude lo invoca como módulo):
    from scripts.import_jobs import import_jobs
    import_jobs([
        {"title": "...", "company": "...", "location": "...", "url": "...", "description": "..."},
        ...
    ])

Dedup: por URL exacta (LinkedIn repite la misma oferta en varias alertas/digests).
Si una oferta ya existe se actualiza la fecha de "vista por última vez" pero no se
duplica ni se pisa su estado (nuevo/aplicado) ni sus fechas de importación originales.
"""
import json
import re
from datetime import date, datetime
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
JOBS_PATH = ROOT / "data" / "cache" / "job_postings.json"

JOB_KEYWORDS = {
    "coo": 30, "chief operating officer": 30, "ceo": 30, "chief executive": 30,
    "director general": 30, "directora general": 30, "general manager": 25,
    "managing director": 25, "c-level": 20, "c level": 20,
    "transformación": 20, "transformacion": 20, "transformation": 20,
    "innovación": 15, "innovacion": 15, "innovation": 15,
}


def slugify(text):
    return re.sub(r"[^a-z0-9]+", "-", text.lower()).strip("-")


def score_job(title, description, location):
    text = f"{title} {description}".lower()
    text = re.sub(r"/[ao]\b", "", text)
    score = sum(w for k, w in JOB_KEYWORDS.items() if k in text)
    loc = (location or "").lower()
    location_match = "barcelona" in loc or "remoto" in loc or "remote" in loc
    if not location_match:
        score = max(0, score - 15)
    return min(100, score), location_match


def load_jobs():
    if JOBS_PATH.exists():
        return json.loads(JOBS_PATH.read_text(encoding="utf-8"))
    return []


def save_jobs(jobs):
    JOBS_PATH.parent.mkdir(parents=True, exist_ok=True)
    JOBS_PATH.write_text(json.dumps(jobs, ensure_ascii=False, indent=2), encoding="utf-8")


def import_jobs(raw_jobs, source="email_linkedin"):
    """raw_jobs: lista de dicts con title/company/location/url/description.
    Devuelve (nuevas, vistas_de_nuevo) — cuántas se añadieron vs cuántas ya existían."""
    jobs = load_jobs()
    existing_urls = {j["url"] for j in jobs if j.get("url")}
    now = datetime.now().isoformat(timespec="seconds")
    today = date.today().isoformat()

    added, seen_again = 0, 0
    for raw in raw_jobs:
        url = raw.get("url")
        if url and url in existing_urls:
            for j in jobs:
                if j.get("url") == url:
                    j["last_seen_on"] = today
            seen_again += 1
            continue
        score, location_match = score_job(raw["title"], raw.get("description", ""), raw["location"])
        jobs.append({
            "id": f"job-{len(jobs)}-{slugify(raw['title'])}",
            "title": raw["title"], "company": raw["company"], "location": raw["location"],
            "url": url, "description": raw.get("description", ""), "score": score,
            "location_match": location_match, "status": "nuevo", "source": source,
            "imported_on": now, "last_seen_on": today,
        })
        if url:
            existing_urls.add(url)
        added += 1

    save_jobs(jobs)
    return added, seen_again
