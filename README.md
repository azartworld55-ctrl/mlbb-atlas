# Land of Legends

**Live website:** https://azartworld55-ctrl.github.io/mlbb-atlas/

Land of Legends — независимый фанатский справочник Mobile Legends: Bang Bang с каталогом героев, записями навыков по патчам, эмблемами, боевыми заклинаниями и инструментами анализа.

> **Неофициальный проект.** Land of Legends не связан с Moonton. Названия, игровые материалы и изображения принадлежат их правообладателям.

## Что есть на сайте

- Каталог героев с поиском, фильтрами по ролям и линиям, карточками и избранным.
- Записи параметров навыков с привязкой к версии/каналу патча и отметкой достоверности.
- Справочник эмблем и боевых заклинаний.
- Раздел источников, показывающий ссылки, сохранённые в наборах данных.
- Сравнение героев и личный тир-лист.
- Локальный конструктор сборок и калькулятор для поддерживаемых записей.
- Адаптивный интерфейс для телефона и компьютера; избранное, сборки и тир-лист хранятся в браузере.

Данные сообщества могут быть неполными или не соответствовать последней версии клиента. Статусы и ссылки на источники следует проверять перед использованием результатов.

## Репозиторий и сайт

- **Сайт:** https://azartworld55-ctrl.github.io/mlbb-atlas/
- **Исходный код:** https://github.com/azartworld55-ctrl/mlbb-atlas
- **История изменений:** https://github.com/azartworld55-ctrl/mlbb-atlas/commits/main
- **Проверки и публикации:** https://github.com/azartworld55-ctrl/mlbb-atlas/actions

Имя репозитория оставлено `mlbb-atlas`, чтобы сохранить действующий адрес GitHub Pages. Название самого проекта и сайта — **Land of Legends**.

## Структура

```text
backend/       FastAPI-приложение и логика API
data/          Наборы данных с версиями и источниками
docs/          Модель данных, правила и исследовательские заметки
site/          Статический сайт для GitHub Pages
scripts/       Сборка локализации и проверки
tests/         Автоматические тесты
.github/       GitHub Actions для проверок и публикации
```

## Локальный запуск API

Требуется Python 3.11+:

```bash
python -m venv .venv
source .venv/bin/activate
pip install -e ".[dev]"
uvicorn app.main:app --app-dir backend --reload
```

API docs после запуска: http://127.0.0.1:8000/docs

Запуск тестов:

```bash
pytest
```

## API v1

- `GET /api/v1/health`
- `GET /api/v1/meta`
- `GET /api/v1/heroes`
- `GET /api/v1/heroes/{hero_id}`
- `GET /api/v1/items` и `GET /api/v1/items/{item_id}`
- `GET /api/v1/emblems`
- `GET /api/v1/spells`
- `GET /api/v1/skill-versions`
- `GET /api/v1/skill-versions/{record_id}`
- `POST /api/v1/calculator/evaluate`
- `POST /api/v1/calculator/matchup-preview`

## Источники и достоверность

Каждая запись должна сохранять источник, дату получения, версию игры и статус достоверности: `verified`, `reported` или `experimental`. Импортированные сведения не следует считать независимо проверенными. Подробности — в [политике данных](docs/data-policy.md), [модели данных](docs/canonical-data-model.md), [инструкции импорта](docs/data-import.md), [аудите источников навыков](docs/upstream-source-audit.md) и [уведомлениях о сторонних материалах](THIRD_PARTY_NOTICES.md).

## Лицензия

Исходный код проекта распространяется по MIT. Это не предоставляет прав на товарные знаки Mobile Legends, игровые материалы, изображения или сторонние наборы данных.
