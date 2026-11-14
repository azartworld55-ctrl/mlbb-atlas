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
- `GET /api/v1/items`

Collections intentionally start empty. The API does not invent missing game values.

## Data quality

Every factual record must include a source, retrieval date, game version and confidence status (`verified`, `reported` or `experimental`). Exact skill scaling and damage formulas must not be inferred from descriptive text; mark them experimental until independently tested. See [data policy](docs/data-policy.md), [formula format](docs/formula-format.md) and [source register](data/sources/README.md).

## Combining upstream projects

MLBB Atlas uses existing public projects as research references and potential data sources, not as material to copy indiscriminately. Before importing code, datasets, text or artwork, inspect the exact license and terms, preserve required attribution, and record provenance. A public GitHub repository or topic page is not automatically reusable.

## Contributing

A useful report includes the game patch, source or repeatable test method, proposed change, and any uncertainty or mode/platform differences.

## License

Original code in this repository is MIT licensed. That license does not grant rights to MLBB trademarks, game content, images or third-party datasets.
