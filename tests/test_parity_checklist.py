"""Public parity checklist contract tests."""

from pathlib import Path


PARITY_CHECKLIST = Path("docs/parity-checklist.md")


def test_parity_checklist_is_public_safe_and_linked() -> None:
    """Test the production-parity checklist exists and is wired into release docs."""
    checklist = PARITY_CHECKLIST.read_text(encoding="utf-8")
    readme = Path("README.md").read_text(encoding="utf-8")
    release_checklist = Path("docs/release-checklist.md").read_text(encoding="utf-8")
    alpha_plan = Path("docs/alpha-test-plan.md").read_text(encoding="utf-8")

    assert "docs/parity-checklist.md" in readme
    assert "docs/parity-checklist.md" in release_checklist
    assert "docs/parity-checklist.md" in alpha_plan

    required_sections = [
        "## Scope",
        "## Status Legend",
        "## Queue And State",
        "## Services And Command Safety",
        "## Runtime Reconciliation",
        "## Dashboard Card",
        "## Release Gates",
    ]
    for section in required_sections:
        assert section in checklist

    for status in ["Ported", "Runtime validated", "Deferred", "Obsolete"]:
        assert f"`{status}`" in checklist

    forbidden_fragments = [
        "haos.lan",
        "root@",
        "/home/fredrik",
        "access_token",
        "bearer ",
        "musse",
        "köket",
        "hallen",
    ]
    normalized = checklist.lower()
    for fragment in forbidden_fragments:
        assert fragment not in normalized, f"{fragment!r} leaked through {PARITY_CHECKLIST}"


def test_parity_checklist_tracks_required_beta_gates() -> None:
    """Test the checklist preserves the major migration gates."""
    checklist = PARITY_CHECKLIST.read_text(encoding="utf-8")

    required_rows = [
        "| Queue add room |",
        "| Queue start |",
        "| Mid-run pending edits |",
        "| Command gate disabled by default |",
        "| Running override controls |",
        "| Recoverable robot errors |",
        "| Mop remove/install maintenance |",
        "| Read-only HACS alpha install |",
        "| Controlled command smoke |",
        "| Cutover issue exists |",
    ]
    for row in required_rows:
        assert row in checklist
