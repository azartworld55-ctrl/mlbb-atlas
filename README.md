# MLBB Atlas

An open-source, community-maintained Mobile Legends: Bang Bang reference database, website and API.

> **Unofficial project.** MLBB and related game assets belong to their respective owners. This project is not affiliated with or endorsed by Moonton.

## Goals

- Version-aware catalogues for heroes, skills, equipment, emblems and battle spells.
- A public REST API and browser interface.
- Source attribution and confidence labels for every factual record.
- Reproducible scaling and damage calculations, backed by tests.
- Patch history and community corrections.

## Structure

```text
backend/          FastAPI application and domain logic
data/             Versioned, source-attributed JSON datasets
docs/             Data policy and research notes
frontend/         Static web client
tests/            Automated tests
```

## Quick start

Python 3.11+:

```bash
python -m venv .venv
# Windows: .venv\\Scripts\\activate
source .venv/bin/activate
pip install -e ".[dev]"
uvicorn app.main:app --app-dir backend --reload
```

Website: http://127.0.0.1:8000 · API docs: http://127.0.0.1:8000/docs

Run tests with `pytest`.

## API v1

- `GET /api/v1/health`
- `GET /api/v1/meta`
- `GET /api/v1/heroes`
- `GET /api/v1/heroes/{hero_id}`
- `GET /api/v1/items` and `GET /api/v1/items/{item_id}`
- `GET /api/v1/emblems`
- `GET /api/v1/spells`
- `POST /api/v1/calculator/evaluate` — evaluates a caller-supplied JSON formula without assuming unverified in-game mechanics

The initial import currently contains 133 heroes, 89 items and 7 emblems. Battle spells remain empty until a suitable source is reviewed. The calculator currently provides a formula sandbox only; it is not yet a verified in-game damage simulator. Imported values are labelled `reported`, not independently verified.

## Data quality

Every factual record must include a source, retrieval date, game version and confidence status (`verified`, `reported` or `experimental`). Exact skill scaling and damage formulas must not be inferred from descriptive text; mark them experimental until independently tested. See [data policy](docs/data-policy.md), [canonical data model](docs/canonical-data-model.md), [import workflow](docs/data-import.md), [formula format](docs/formula-format.md), [skill-source audit](docs/upstream-source-audit.md), [source register](data/sources/README.md) and [third-party notices](THIRD_PARTY_NOTICES.md).

## Combining upstream projects

The first normalized dataset import is derived from [p3hndrx/MLBB-API](https://github.com/p3hndrx/MLBB-API), under its MIT license, with source snapshots, blob SHAs and attribution retained in this repository. The [MLBB-Hero-Scraper](https://github.com/warungerik/MLBB-Hero-Scraper) is documented as a candidate metadata collection reference; its code is not copied. Every other source must be reviewed independently. The initial cross-source audit and the community-reported Original Server patch 2.2.23 record (2026-11-11) are documented separately; this does not mean all hero skills have been imported or verified. See [skill-source audit](docs/upstream-source-audit.md), [patch record](data/patches/2.2.23.json) and [third-party notices](THIRD_PARTY_NOTICES.md).

## Contributing

A useful report includes the game patch, source or repeatable test method, proposed change, and any uncertainty or mode/platform differences.

## License

Original code in this repository is MIT licensed. That license does not grant rights to MLBB trademarks, game content, images or third-party datasets.
