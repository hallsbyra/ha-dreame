"""Development runner contract tests."""

from pathlib import Path


def test_docker_dev_runner_is_the_documented_local_entrypoint() -> None:
    """Test local validation is routed through Docker instead of host runtimes."""
    dockerfile = Path("Dockerfile.dev")
    runner = Path("scripts/dev")
    readme = Path("README.md").read_text(encoding="utf-8")
    agents = Path("AGENTS.md").read_text(encoding="utf-8")

    assert dockerfile.exists()
    assert runner.exists()
    assert "Python 3.13" in readme
    assert "Node 22" in readme
    assert "./scripts/dev check" in readme
    assert "./scripts/dev python-check" in agents
    assert "./scripts/dev frontend-check" in agents


def test_github_validate_workflow_uses_the_docker_dev_runner() -> None:
    """Test CI validation uses the same Docker entrypoints as local development."""
    workflow = Path(".github/workflows/validate.yml").read_text(encoding="utf-8")

    assert "./scripts/dev python-check" in workflow
    assert "./scripts/dev frontend-check" in workflow
    assert "actions/setup-python" not in workflow
    assert "actions/setup-node" not in workflow
