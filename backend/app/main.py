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
