"""Tests for repository packaging metadata."""

import json
from pathlib import Path

from custom_components.ha_dreame.const import DOMAIN, TITLE


def test_manifest_matches_domain_and_title() -> None:
    """Test the manifest exposes the expected custom integration identity."""
    manifest = json.loads(Path("custom_components/ha_dreame/manifest.json").read_text())

    assert manifest["domain"] == DOMAIN
    assert manifest["name"] == TITLE
    assert manifest["config_flow"] is True
    assert manifest["version"]


def test_hacs_manifest_is_integration_repo() -> None:
    """Test the repository has the expected HACS integration layout."""
    hacs_manifest = json.loads(Path("hacs.json").read_text())

    assert hacs_manifest["name"] == TITLE
    assert hacs_manifest["content_in_root"] is False
    assert Path("custom_components", DOMAIN, "manifest.json").is_file()
