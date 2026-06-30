from pathlib import Path

FORBIDDEN_IMPORTS = ("import requests", "import httpx", "import urllib", "from urllib")


def test_app_has_no_runtime_network_clients():
    for root in (Path("backend"), Path("frontend")):
        paths = root.rglob("*.py")
        for path in paths:
            source = path.read_text(encoding="utf-8")
            assert not any(forbidden in source for forbidden in FORBIDDEN_IMPORTS), path
