"""Public documentation contract tests."""

from pathlib import Path


README = Path("README.md")


def test_readme_documents_alpha_install_remove_limitations() -> None:
    """Test README covers the alpha information needed for public HACS testing."""
    readme = README.read_text(encoding="utf-8")

    required_sections = [
        "## Installation",
        "## Configuration",
        "## Dashboard Card",
        "## Safety Model",
        "## Current Limitations",
        "## Removal",
        "## Validation",
    ]
    for section in required_sections:
        assert section in readme

    required_public_details = [
        "HACS",
        "dreame_vacuum",
        "allow_robot_commands",
        "auto_reconcile_enabled",
        "/ha_dreame/frontend/ha-dreame-queue-card.js",
        "custom:ha-dreame-queue-card",
        "sensor.ha_dreame_queue_status",
    ]
    for detail in required_public_details:
        assert detail in readme


def test_readme_avoids_private_runtime_assumptions() -> None:
    """Test README does not publish private runtime details."""
    readme = README.read_text(encoding="utf-8").lower()

    forbidden_fragments = [
        "haos.lan",
        "root@",
        "/home/fredrik",
        "token",
        "secret",
    ]
    for fragment in forbidden_fragments:
        assert fragment not in readme
