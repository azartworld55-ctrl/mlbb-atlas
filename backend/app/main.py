"""MLBB Atlas API and static website."""
from pathlib import Path

from fastapi import FastAPI, HTTPException, Query
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel, Field

from app.data import find_record, load_collection
from app.formulas import evaluate_expression

class FormulaEvaluationRequest(BaseModel):
    """A caller-supplied, non-executable formula and its numeric inputs."""

    expression: dict
    stats: dict[str, object] = Field(default_factory=dict)
    formula_id: str | None = None
    game_patch: str | None = None


ROOT = Path(__file__).resolve().parents[2]
FRONTEND = ROOT / "frontend"
COLLECTIONS = ("heroes", "items", "emblems", "spells")

app = FastAPI(
    title="MLBB Atlas API",
    description="Unofficial, source-attributed Mobile Legends: Bang Bang reference API.",
    version="0.1.0",
)
if FRONTEND.exists():
    app.mount("/assets", StaticFiles(directory=FRONTEND), name="assets")


@app.get("/", include_in_schema=False)
def home():
    index = FRONTEND / "index.html"
    if not index.exists():
        raise HTTPException(status_code=404, detail="Website files are not installed")
    return FileResponse(index)


@app.get("/api/v1/health", tags=["system"])
def health():
    return {"status": "ok", "project": "mlbb-atlas", "api_version": "v1"}


@app.get("/api/v1/meta", tags=["system"])
def metadata():
    return {
        "project_version": "0.1.0",
        "collections": {name: len(load_collection(name)) for name in COLLECTIONS},
    }


@app.get("/api/v1/heroes", tags=["heroes"])
def heroes(
    role: str | None = Query(default=None),
    lane: str | None = Query(default=None),
    search: str | None = Query(default=None, min_length=1, max_length=80),
):
    records = load_collection("heroes")
    if role:
        records = [r for r in records if role.casefold() in [x.casefold() for x in r.get("roles", [])]]
    if lane:
        records = [r for r in records if lane.casefold() in [x.casefold() for x in r.get("lanes", [])]]
    if search:
        needle = search.casefold()
        records = [r for r in records if needle in r.get("name", "").casefold()]
    return {"count": len(records), "data": records}


@app.get("/api/v1/heroes/{hero_id}", tags=["heroes"])
def hero_detail(hero_id: str):
    record = find_record("heroes", hero_id)
    if record is None:
        raise HTTPException(status_code=404, detail="Hero not found")
    return record


@app.get("/api/v1/items", tags=["items"])
def items(
    category: str | None = Query(default=None),
    search: str | None = Query(default=None, min_length=1, max_length=80),
):
    records = load_collection("items")
    if category:
        records = [r for r in records if r.get("category", "").casefold() == category.casefold()]
    if search:
        needle = search.casefold()
        records = [r for r in records if needle in r.get("name", "").casefold()]
    return {"count": len(records), "data": records}


@app.get("/api/v1/items/{item_id}", tags=["items"])
def item_detail(item_id: str):
    record = find_record("items", item_id)
    if record is None:
        raise HTTPException(status_code=404, detail="Item not found")
    return record


@app.get("/api/v1/emblems", tags=["emblems"])
def emblems(search: str | None = Query(default=None, min_length=1, max_length=80)):
    records = load_collection("emblems")
    if search:
        needle = search.casefold()
        records = [r for r in records if needle in r.get("name", "").casefold()]
    return {"count": len(records), "data": records}


@app.post("/api/v1/calculator/evaluate", tags=["calculator"])
def evaluate_formula(payload: FormulaEvaluationRequest):
    """Evaluate a safe JSON expression; no MLBB mitigation rules are implied."""
    try:
        value = evaluate_expression(payload.expression, payload.stats)
    except (TypeError, ValueError) as exc:
        raise HTTPException(status_code=422, detail=str(exc)) from exc
    return {
        "formula_id": payload.formula_id,
        "game_patch": payload.game_patch,
        "value": value,
        "calculation_scope": "supplied_expression_only",
        "confidence": "user_supplied_unverified",
        "note": "This is only the result of the supplied expression; no in-game damage, defense, rounding, or special mechanics are inferred.",
    }


@app.get("/api/v1/spells", tags=["spells"])
def spells(search: str | None = Query(default=None, min_length=1, max_length=80)):
    records = load_collection("spells")
    if search:
        needle = search.casefold()
        records = [r for r in records if needle in r.get("name", "").casefold()]
    return {"count": len(records), "data": records}


@app.get("/api/v1/skill-versions", tags=["skills"])
def skill_versions(
    hero_id: str | None = Query(default=None, min_length=1, max_length=80),
    skill_id: str | None = Query(default=None, min_length=1, max_length=100),
    patch: str | None = Query(default=None, min_length=1, max_length=40),
    channel: str | None = Query(default=None, min_length=1, max_length=40),
    verification_status: str | None = Query(default=None, min_length=1, max_length=40),
):
    """Return patch-scoped skill parameters without inventing missing rank values."""
    path = ROOT / "data" / "skill_versions" / "current.json"
    if not path.exists():
        return {"count": 0, "data": []}
    import json

    with path.open("r", encoding="utf-8") as stream:
        records = json.load(stream)
    if not isinstance(records, list):
        raise HTTPException(status_code=500, detail="Skill version dataset must be a JSON array")

    if hero_id:
        records = [r for r in records if r.get("hero_id", "").casefold() == hero_id.casefold()]
    if skill_id:
        records = [r for r in records if r.get("skill_id", "").casefold() == skill_id.casefold()]
    if patch:
        records = [r for r in records if r.get("patch", {}).get("version", "").casefold() == patch.casefold()]
    if channel:
        records = [r for r in records if r.get("patch", {}).get("channel", "").casefold() == channel.casefold()]
    if verification_status:
        records = [r for r in records if r.get("verification", {}).get("status", "").casefold() == verification_status.casefold()]
    records.sort(key=lambda r: (r.get("hero_id", ""), r.get("skill_id", ""), r.get("patch", {}).get("effective_from", "")))
    return {"count": len(records), "data": records}


@app.get("/api/v1/skill-versions/{record_id}", tags=["skills"])
def skill_version_detail(record_id: str):
    """Return one exact patch-scoped skill record."""
    result = skill_versions()
    for record in result["data"]:
        if record.get("record_id") == record_id:
            return record
    raise HTTPException(status_code=404, detail="Skill version record not found")


class MatchupSideRequest(BaseModel):
    hero_id: str
    item_ids: list[str] = Field(default_factory=list, max_length=6)
    emblem_id: str | None = None
    spell_id: str | None = None
    buffs: dict[str, bool] = Field(default_factory=lambda: {"blue": False, "red": False})
    total_physical_attack: float = 0
    total_magic_power: float = 0
    physical_defense: float = 0
    magic_defense: float = 0


class MatchupPreviewRequest(BaseModel):
    attacker: MatchupSideRequest
    defender: MatchupSideRequest
    skill_record_id: str | None = None
    endpoint: str = "high"


def _numeric_modifier(value):
    if isinstance(value, bool) or value is None:
        return None
    if isinstance(value, (int, float)):
        return float(value)
    if isinstance(value, str):
        cleaned = value.strip().replace("%", "")
        try:
            return float(cleaned)
        except ValueError:
            return None
    return None


def _build_side_preview(side, label):
    heroes = load_collection("heroes")
    hero = next((row for row in heroes if row.get("slug") == side.hero_id or row.get("id") == side.hero_id), None)
    if hero is None:
        raise HTTPException(status_code=404, detail=f"{label}: hero not found")

    items = load_collection("items")
    selected_items = []
    totals = {"physical_attack": side.total_physical_attack, "magic_power": side.total_magic_power}
    for item_id in side.item_ids:
        item = next((row for row in items if row.get("id") == item_id or row.get("slug") == item_id), None)
        if item is None:
            raise HTTPException(status_code=404, detail=f"{label}: item {item_id} not found")
        selected_items.append(item)
        for group in item.get("modifiers", []):
            if isinstance(group, dict):
                for key, raw in group.items():
                    value = _numeric_modifier(raw)
                    if value is not None:
                        totals[key] = totals.get(key, 0) + value

    emblem = None
    if side.emblem_id:
        emblems = load_collection("emblems")
        emblem = next((row for row in emblems if row.get("id") == side.emblem_id or row.get("slug") == side.emblem_id), None)
        if emblem is None:
            raise HTTPException(status_code=404, detail=f"{label}: emblem not found")
        for group in emblem.get("modifiers", []):
            if isinstance(group, dict):
                for key, raw in group.items():
                    value = _numeric_modifier(raw)
                    if value is not None:
                        totals[key] = totals.get(key, 0) + value

    spell = None
    if side.spell_id:
        spells = load_collection("spells")
        spell = next((row for row in spells if row.get("id") == side.spell_id or row.get("slug") == side.spell_id), None)
        if spell is None:
            raise HTTPException(status_code=404, detail=f"{label}: battle spell not found")

    return {
        "hero": {"id": hero.get("id"), "slug": hero.get("slug"), "name": hero.get("name")},
        "items": [{"id": item.get("id"), "slug": item.get("slug"), "name": item.get("name")} for item in selected_items],
        "emblem": {"id": emblem.get("id"), "name": emblem.get("name")} if emblem else None,
        "spell": spell,
        "buffs": {"blue": bool(side.buffs.get("blue")), "red": bool(side.buffs.get("red"))},
        "stats": totals,
        "defenses": {"physical": totals.get("physical_defense", side.physical_defense), "magic": totals.get("magic_defense", side.magic_defense)},
    }


@app.post("/api/v1/calculator/matchup-preview", tags=["calculator"])
def matchup_preview(payload: MatchupPreviewRequest):
    """Compare two editable loadouts and calculate only sourced, pre-mitigation skill damage."""
    if payload.endpoint not in {"low", "high"}:
        raise HTTPException(status_code=422, detail="endpoint must be 'low' or 'high'")

    attacker = _build_side_preview(payload.attacker, "attacker")
    defender = _build_side_preview(payload.defender, "defender")
    damage = None
    skill = None
    if payload.skill_record_id:
        path = ROOT / "data" / "skill_versions" / "current.json"
        import json
        with path.open("r", encoding="utf-8") as stream:
            records = json.load(stream)
        skill = next((row for row in records if row.get("record_id") == payload.skill_record_id), None)
        if skill is None:
            raise HTTPException(status_code=404, detail="Skill version record not found")
        if skill.get("hero_id", "").casefold() != payload.attacker.hero_id.casefold():
            raise HTTPException(status_code=422, detail="Selected skill record does not belong to the attacking hero")

        base_values = []
        scaling_total = 0.0
        unsupported = []
        for parameter in skill.get("parameters", []):
            values = parameter.get("values_by_skill_level", [])
            semantics = parameter.get("value_semantics")
            if not values or semantics not in {"fixed", "endpoints", "per_level"}:
                continue
            index = 0 if payload.endpoint == "low" else len(values) - 1
            value = float(values[index])
            if parameter.get("kind") == "base_damage":
                base_values.append(value)
            elif parameter.get("kind") == "scaling":
                attribute = parameter.get("scaling_attribute")
                stat_key = {"physical_attack": "physical_attack", "magic_power": "magic_power", "max_hp": "hp"}.get(attribute)
                if stat_key:
                    scaling_total += attacker["stats"].get(stat_key, 0) * value / 100
                else:
                    unsupported.append(parameter.get("key", "unknown scaling"))
        if base_values:
            damage = sum(base_values) + scaling_total
        skill = {
            "record_id": skill.get("record_id"),
            "hero_id": skill.get("hero_id"),
            "skill_name": skill.get("skill_name"),
            "patch": skill.get("patch"),
            "verification": skill.get("verification"),
            "damage_type": next((p.get("damage_type") for p in skill.get("parameters", []) if p.get("kind") == "base_damage" and p.get("damage_type")), None),
            "damage_before_defense": damage,
            "unsupported_scalings": unsupported,
            "endpoint_used": payload.endpoint,
            "note": "This is a source-parameter preview before enemy defense, penetration, damage reduction, shields, and conditional effects. It is not a full in-game damage result.",
        }

    return {
        "attacker": attacker,
        "defender": defender,
        "skill": skill,
        "damage_before_defense": damage,
        "calculation_scope": "source_parameter_preview_before_defense",
        "buff_note": "Blue/red buff selections are saved as scenario flags; their combat modifiers are not applied until patch-specific values are verified.",
        "spell_note": "Battle spells are selectable for both sides; their active effects are not added to skill damage in this preview.",
    }
