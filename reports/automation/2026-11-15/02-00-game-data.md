# Отчёт автоматического обновления игровых данных — 2026-11-15

## Статус

Изменения влиты в `main` через [PR #1](https://github.com/azartworld55-ctrl/mlbb-atlas/pull/1). Итоговый merge-коммит: [c069bfaff54f6dbdfe398ef00b1611424e884fb0](https://github.com/azartworld55-ctrl/mlbb-atlas/commit/c069bfaff54f6dbdfe398ef00b1611424e884fb0). GitHub Actions tests, source comparison и GitHub Pages deploy завершились успешно.

## Состояние репозитория перед работой

- Ветка: `main`.
- Исходный HEAD: [d44c4b01feecb2afa73644480842be9e4a1be084](https://github.com/azartworld55-ctrl/mlbb-atlas/commit/d44c4b01feecb2afa73644480842be9e4a1be084).
- Последний коммит: `Keep build fragments out of deployed website`.
- До начала работы открытых PR не было.
- Последние тесты и Pages deployment на исходном HEAD завершились успешно.
- Каталог до обновления: 133 героя, 89 предметов, 7 наборов базовых характеристик эмблем, 12 боевых заклинаний и 26 patch-scoped записей навыков.

## Проверка версии игры и источников

Целевая версия — **Original Server 2.2.23**, дата выпуска **11 ноября 2026**. Community-архив MLBBHub на момент проверки также указывает Advance Server 2.2.32 как тестовую ветку. Её изменения не переносились в Original Server.

Прямую публикацию патчноута на официальном домене или канале Moonton в этом запуске подтвердить не удалось. Поэтому статус версии в данных оставлен `community_reported_pending_official_confirmation`, а все новые значения помечены `reported`, не `verified`.

Использованные источники:

1. [Полный пост с патчноутом 2.2.23 в r/MobileLegendsGame](https://www.reddit.com/r/MobileLegendsGame/comments/1xtm2m3/patch_notes_2223_org_server/) — публикация от имени модератора сообщества u/Tigreal, дата обновления 11.11.2026. Это community repost, не прямая публикация Moonton.
2. [Liquipedia — Patch 2.2.23](https://liquipedia.net/mobilelegends/Patch_2.2.23) — независимая community-wiki сверка версии, даты и описаний.
3. [MLBBHub — Original Server patch archive](https://mlbbhub.com/patch-notes/original/2.2.23) — дополнительная сверка патча и отдельных значений.
4. [Официальный сайт MLBB](https://www.mobilelegends.com/) — проверялся как возможный первичный источник; прямую страницу числового патчноута 2.2.23 найти не удалось.

Источники 1–3 не считаются официальными источниками Moonton. Значения не подтверждались отдельным тестом в клиенте игры.

## Что изменено

### Предметы

- **Antique Cuirass / Deter:** снижение физического урона атакующего обновлено с 6% до 8%.
- **Chastise Pauldron / Chastise:** ограничение скорости атаки атакующего и её предела обновлено с 75% до 80% от обычного значения.
- Для обоих предметов добавлен отдельный объект `patch_updates` с версией, датой, значениями до/после и ссылками. Исходная upstream provenance сохранена.

### Боевые заклинания

- **Sprint:** текущее значение перезарядки уже было 75 секунд. Добавлена явная запись истории 100 → 75 секунд для патча 2.2.23 и источник изменения.

### Навыки героев

- Добавлена patch-scoped запись **Masha / Primal Pact**: компоненты формулы дополнительного урона когтей и диапазон восстановления HP 3–6% Max HP. Диапазон оставлен endpoints — промежуточные значения по уровням не выдумывались.
- Для **Masha / Claw Strike** добавлены замедление героя на 50% на 1 секунду и уменьшение ширины пути на 20%.
- Для **Freya / Valkyrie Descent** добавлен новый эффект: 30 Movement Speed во время действия Ultimate.
- Добавлена patch-scoped запись **Melissa / Eyes on You!**: Muddles Damage Transfer и Attack Effect Inheritance Ratio — 50–60%. Промежуточные значения по уровням не интерполировались.
- Общее число записей навыков выросло с 26 до 28.

### Каталог героев

- В описании пассивного навыка Masha исправлены коэффициенты дополнительного урона и диапазон восстановления HP; в Claw Strike добавлены slow и уменьшение ширины пути.
- Для Melissa добавлена запись об изменениях двух коэффициентов Muddles.
- Для Kaja добавлена история изменений Soaring и Divine Binding без выдумывания числовых значений.
- Для Uranus зафиксировано изменение типа урона от splash Basic Attack на Magic Damage. Текущий текст каталога уже указывал Magic Damage, поэтому неподтверждённые числовые значения не менялись.

### Патч, эмблемы и поле боя

- В `data/patches/2.2.23.json` добавлены числовые изменения предметов, Sprint, таланта Concussive Blast, Gold Lane Siege Minion и Golden Turret.
- Добавлены отдельные описательные записи для реворка Popol и Kupa, поведенческих изменений Kaja и Karrie, визуальной корректировки Kagura, изменения типа урона Uranus и Healing Turtle.
- **Базовые характеристики 7 эмблем не менялись.** Concussive Blast относится к таланту эмблемы, а не к базовым характеристикам набора; поэтому он записан в истории патча, а не искусственно добавлен в текущую структуру эмблем.
- Brawl-only модификаторы не перенесены в стандартные характеристики героев.

## Что осталось неподтверждённым или неполным

- Полный набор навыков Popol и Kupa в каталоге всё ещё содержит прежнюю структуру. Для безопасной замены нужны полная карта форм/групп и точные значения всех навыков; текст патчноута не даёт достаточной структуры.
- Kaja и часть изменений Karrie описаны патчноутом без точных числовых значений; записаны только как качественные изменения.
- Значения 2.2.23 остаются community-reported, поскольку нет подтверждённой прямой публикации Moonton и отдельного теста в Original Server.
- Значения Advance Server 2.2.32 не смешивались с Original Server 2.2.23.

## Проверки

- JSON-файлы изменённого каталога повторно прочитаны и успешно разобраны.
- Добавлен regression test `test_patch_2_2_23_updates_are_reflected_in_catalogues`.
- GitHub Actions `tests` для исходного PR HEAD до добавления этого отчёта завершился успешно: [run 43655505806](https://github.com/azartworld55-ctrl/mlbb-atlas/actions/runs/43655505806).
- После добавления отчёта GitHub Actions tests для PR завершился успешно: [run 43655594578](https://github.com/azartworld55-ctrl/mlbb-atlas/actions/runs/43655594578). После merge в `main` повторные проверки завершились успешно: [tests run 43655638112](https://github.com/azartworld55-ctrl/mlbb-atlas/actions/runs/43655638112), [skill-source comparison run 43655638056](https://github.com/azartworld55-ctrl/mlbb-atlas/actions/runs/43655638056), [GitHub Pages deploy run 43655638004](https://github.com/azartworld55-ctrl/mlbb-atlas/actions/runs/43655638004). Pages deployment completed successfully.

## Коммиты и PR

- Герои: [35c651f](https://github.com/azartworld55-ctrl/mlbb-atlas/commit/35c651f0f2047df382c205a9d307963eeadf318e)
- Версионные навыки: [24fc88d](https://github.com/azartworld55-ctrl/mlbb-atlas/commit/24fc88d5e867b3409c30b8ef862c39b5b6b02df7)
- Предметы: [c356cc6](https://github.com/azartworld55-ctrl/mlbb-atlas/commit/c356cc6412bf22e9fc62ca6b9c719934a03e4aa0)
- Боевые заклинания: [bdf83aa](https://github.com/azartworld55-ctrl/mlbb-atlas/commit/bdf83aae67ef4bd321f583ea16fe12680f0b7e19)
- История патча: [bcd5fb0](https://github.com/azartworld55-ctrl/mlbb-atlas/commit/bcd5fb01b0d151b95deb85794435ec48d488dc3a)
- Регрессионный тест: [6d25bfd](https://github.com/azartworld55-ctrl/mlbb-atlas/commit/6d25bfd01213c809e430ac5904634d96f0b3c0a1)
- Документация аудита источников: [2297539](https://github.com/azartworld55-ctrl/mlbb-atlas/commit/2297539a4457b1166a9b4d65f61bef212d85102d)
- PR: [Update Original Server patch 2.2.23 data](https://github.com/azartworld55-ctrl/mlbb-atlas/pull/1)


## Итог после merge

- PR #1 закрыт со статусом merged.
- Основная ветка `main` содержит merge-коммит [c069bfaff54f6dbdfe398ef00b1611424e884fb0](https://github.com/azartworld55-ctrl/mlbb-atlas/commit/c069bfaff54f6dbdfe398ef00b1611424e884fb0).
- Тесты и валидаторы прошли успешно после merge.
- Сравнение источников навыков прошло успешно; workflow не публикует сырые данные, а только временный отчёт сравнения.
- Сборка и публикация GitHub Pages завершились успешно.
