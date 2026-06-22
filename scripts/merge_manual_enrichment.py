"""Lee data/cache/manual_target_enrichment.json (resultado de la rutina en la nube,
tras git pull) y aplica nombre/empresa/cargo a tu fichero PRIVADO local
manual_reach_targets.json (que nunca sale de tu Mac). Luego vacía los ficheros de
sincronización para que el día siguiente solo se reprocesen los pendientes nuevos.
"""
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
MANUAL_TARGETS_PATH = ROOT / "data" / "cache" / "manual_reach_targets.json"
PENDING_EXPORT_PATH = ROOT / "data" / "cache" / "pending_manual_targets.json"
ENRICHMENT_RESULT_PATH = ROOT / "data" / "cache" / "manual_target_enrichment.json"


def merge():
    if not ENRICHMENT_RESULT_PATH.exists():
        return 0
    enrichment = json.loads(ENRICHMENT_RESULT_PATH.read_text(encoding="utf-8"))
    if not enrichment:
        return 0

    manual = json.loads(MANUAL_TARGETS_PATH.read_text(encoding="utf-8")) if MANUAL_TARGETS_PATH.exists() else []
    by_id = {m["id"]: m for m in manual}

    applied = 0
    for item in enrichment:
        target = by_id.get(item["id"])
        if not target:
            continue
        target["name"] = item.get("name") or target["name"]
        target["firm"] = item.get("firm") or target["firm"]
        target["role"] = item.get("role") or target.get("role", "")
        target["needs_enrichment"] = False
        applied += 1

    MANUAL_TARGETS_PATH.write_text(json.dumps(manual, ensure_ascii=False, indent=2), encoding="utf-8")

    # Limpia los ficheros de sincronización: lo aplicado ya no necesita estar en el repo público.
    PENDING_EXPORT_PATH.write_text("[]", encoding="utf-8")
    ENRICHMENT_RESULT_PATH.write_text("[]", encoding="utf-8")
    return applied


if __name__ == "__main__":
    n = merge()
    print(f"{n} contactos manuales actualizados localmente.")
