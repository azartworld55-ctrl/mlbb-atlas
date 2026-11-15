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


def test_shared_hero_link_opens_after_data_load_and_browser_back_restores_state():
    source = assembled_app()
    assert "function heroFromHash()" in source
    assert "const sharedHero=heroFromHash()" in source
    assert "openHero(sharedHero,true)" in source
    assert "openHero(k,true)" in source
    assert 'window.addEventListener("popstate"' in source
    assert "history.back()" in source
    assert "history.replaceState" in source
