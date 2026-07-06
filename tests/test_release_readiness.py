"""Release readiness contract tests."""

import json
from pathlib import Path

import yaml


ALPHA_TEST_PLAN = Path("docs/alpha-test-plan.md")
PYRIGHT_CONFIG = Path("pyrightconfig.json")
REPOSITORY_LICENSE = Path("LICENSE")
VALIDATE_WORKFLOW = Path(".github/workflows/validate.yml")


def test_validate_workflow_runs_python_type_validation() -> None:
    """Test CI includes Python type validation through the Docker runner."""
    workflow = yaml.safe_load(VALIDATE_WORKFLOW.read_text(encoding="utf-8"))
    python_steps = workflow["jobs"]["python"]["steps"]

    step_names = {step["name"] for step in python_steps}
    assert "Validate Python" in step_names

    validation_step = next(step for step in python_steps if step["name"] == "Validate Python")
    assert validation_step["run"] == "./scripts/dev python-check"
    assert "python -m pyright" in Path("scripts/dev").read_text(encoding="utf-8")
    assert "pyright==1.1.411" in Path("requirements-dev.txt").read_text(encoding="utf-8")
    assert Path("pyrightconfig.json").is_file()


def test_repository_declares_hacs_compatible_license() -> None:
    """Test the public HACS repository declares an explicit license."""
    assert REPOSITORY_LICENSE.is_file()

    license_text = REPOSITORY_LICENSE.read_text(encoding="utf-8")

    assert license_text.startswith("MIT License")
    assert "Permission is hereby granted" in license_text


def test_pyright_config_scopes_release_type_gate_to_integration_code() -> None:
    """Test the first Python type gate is focused on integration source."""
    config = json.loads(PYRIGHT_CONFIG.read_text(encoding="utf-8"))

    assert config["include"] == ["custom_components/ha_dreame"]
    assert "custom_components/ha_dreame/frontend" in config["exclude"]
    assert config["pythonVersion"] == "3.13"
    assert config["typeCheckingMode"] == "basic"
    assert "reportMissingImports" not in config
    assert "reportMissingModuleSource" not in config


def test_alpha_test_plan_is_linked_and_public_safe() -> None:
    """Test the HA alpha validation runbook is visible and public-safe."""
    plan = ALPHA_TEST_PLAN.read_text(encoding="utf-8")
    readme = Path("README.md").read_text(encoding="utf-8")
    agents = Path("AGENTS.md").read_text(encoding="utf-8")
    release_checklist = Path("docs/release-checklist.md").read_text(encoding="utf-8")

    assert "docs/alpha-test-plan.md" in readme
    assert "docs/alpha-test-plan.md" in agents
    assert "docs/alpha-test-plan.md" in release_checklist

    required_sections = [
        "## Goal",
        "## Preconditions",
        "## Preflight Validation",
        "## HACS Prerelease Versions",
        "## Install Candidate",
        "## Read-Only Smoke Test",
        "## Dashboard Card Smoke Test",
        "## Controlled Command Smoke Test",
        "## Rollback",
        "## Evidence To Capture",
    ]
    for section in required_sections:
        assert section in plan

    required_safety_phrases = [
        "Leave `allow_robot_commands` disabled",
        "Keep the old controller as the production path",
        "Do not let two controllers send robot commands",
        "docs/dreame-behavior-knowledge.md",
    ]
    for phrase in required_safety_phrases:
        assert phrase in plan


def test_alpha_docs_explain_hacs_prerelease_flow() -> None:
    """Test alpha docs explain how prerelease tags surface in HACS."""
    plan = ALPHA_TEST_PLAN.read_text(encoding="utf-8")
    readme = Path("README.md").read_text(encoding="utf-8")
    release_checklist = Path("docs/release-checklist.md").read_text(encoding="utf-8")

    required_fragments = [
        "GitHub prerelease",
        "enable beta or prerelease visibility",
        "explicitly select the alpha tag",
        "installed version",
    ]
    for fragment in required_fragments:
        assert fragment in plan

    assert "enable beta or prerelease visibility" in readme
    assert "HACS prerelease visibility" in release_checklist


def test_public_release_docs_avoid_private_runtime_details() -> None:
    """Test release-facing docs do not publish private runtime details."""
    public_files = [
        Path("README.md"),
        Path("AGENTS.md"),
        Path("docs/current-state.md"),
        Path("docs/parallel-install.md"),
        Path("docs/release-checklist.md"),
        ALPHA_TEST_PLAN,
    ]
    forbidden_fragments = [
        "haos.lan",
        "root@",
        "/home/fredrik",
        "access_token",
        "bearer ",
        "musse",
        "hallsbyra.se",
    ]

    for path in public_files:
        normalized = path.read_text(encoding="utf-8").lower()
        for fragment in forbidden_fragments:
            assert fragment not in normalized, f"{fragment!r} leaked through {path}"
