"""Exporta SOLO id+URL+camino (nada de nombre/empresa/why/estrategia) de los contactos
manuales pendientes de identificar, a data/cache/pending_manual_targets.json — el único
fichero de Reach que se sincroniza con el repo público, para que la rutina en la nube
pueda identificarlos sin que el resto de tu estrategia salga de tu Mac.
"""
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
MANUAL_TARGETS_PATH = ROOT / "data" / "cache" / "manual_reach_targets.json"
PENDING_EXPORT_PATH = ROOT / "data" / "cache" / "pending_manual_targets.json"


def export_pending():
    manual = json.loads(MANUAL_TARGETS_PATH.read_text(encoding="utf-8")) if MANUAL_TARGETS_PATH.exists() else []
    pending = [
        {"id": m["id"], "linkedin_url": m["linkedin_url"], "camino": m.get("camino")}
        for m in manual if m.get("needs_enrichment")
    ]
    PENDING_EXPORT_PATH.write_text(json.dumps(pending, ensure_ascii=False, indent=2), encoding="utf-8")
    return len(pending)


if __name__ == "__main__":
    n = export_pending()
    print(f"{n} contactos pendientes exportados a {PENDING_EXPORT_PATH}")
