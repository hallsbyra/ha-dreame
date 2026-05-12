"""Tests for repository packaging metadata."""

import json
from pathlib import Path

import yaml

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


def test_quality_scale_tracks_home_assistant_readiness() -> None:
    """Test quality scale tracking lives with the integration."""
    quality_scale = yaml.safe_load(
        Path("custom_components", DOMAIN, "quality_scale.yaml").read_text()
    )

    assert quality_scale["rules"]["config-flow"] == "done"
    assert quality_scale["rules"]["config-flow-test-coverage"] == "done"
    assert quality_scale["rules"]["brands"] == "todo"
