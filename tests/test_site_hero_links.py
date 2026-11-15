from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
FRAGMENTS = [ROOT / "site" / f"app.part{i:02d}.jsfrag" for i in range(1, 6)]


def assembled_app() -> str:
    return "".join(path.read_text(encoding="utf-8") for path in FRAGMENTS)


def test_hero_cards_have_shareable_deep_links():
    source = assembled_app()
    assert 'history.pushState' in source
    assert 'location.hash' in source
    assert 'id="mshare"' in source
    assert "navigator.clipboard.writeText" in source
    assert "\\nif(" not in source


def test_shared_hero_link_opens_after_data_load_and_browser_back_restores_state():
    source = assembled_app()
    assert "function heroFromHash()" in source
    assert "const sharedHero=heroFromHash()" in source
    assert "openHero(sharedHero,true)" in source
    assert "openHero(k,true)" in source
    assert 'window.addEventListener("popstate"' in source
    assert "history.back()" in source
    assert "history.replaceState" in source


def test_service_worker_refreshes_cached_site_shell_after_release():
    worker = (ROOT / "site" / "sw.js").read_text(encoding="utf-8")
    assert 'const CACHE="mlbb-atlas-shell-v4"' in worker


def test_service_worker_only_clears_previous_atlas_shell_caches():
    worker = (ROOT / "site" / "sw.js").read_text(encoding="utf-8")
    assert 'const CACHE="mlbb-atlas-shell-v4"' in worker
    assert 'const CACHE_PREFIX="mlbb-atlas-shell-"' in worker
    assert "keys.filter(k=>k.startsWith(CACHE_PREFIX)&&k!==CACHE)" in worker
