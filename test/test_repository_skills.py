#  Copyright 2020-2026 Karl T Debiec. All rights reserved. This software may be modified
#  and distributed under the terms of the BSD license. See the LICENSE file for details.
"""Behavior and discovery contracts for repository audit skills."""

from __future__ import annotations

import re
from pathlib import Path
from runpy import run_path
from typing import Any

import pytest


@pytest.fixture
def audits() -> dict[str, dict[str, Any]]:
    """Load the standalone helpers without running their command entry points."""
    root = Path(__file__).parents[1] / ".agents/skills"
    return {
        name: run_path(str(root / name / "scripts" / f"{name.replace('-', '_')}.py"))
        for name in ("audit-style", "audit-module-hierarchy")
    }


def test_discoverable_skills_and_relative_links():
    """Keep skill manifests discoverable and their local guide links usable."""
    root = Path(__file__).parents[1]
    assert not (root / "skills").exists()
    for name in ("audit-style", "audit-module-hierarchy"):
        path = root / ".agents/skills" / name / "SKILL.md"
        text = path.read_text(encoding="utf-8")
        assert text.startswith(f"---\nname: {name}\n")
        for link in re.findall(r"\]\(([^)]+)\)", text):
            assert (path.parent / link).resolve().is_file(), link


def test_style_audit_utf8_without_executing_source(
    tmp_path: Path, audits: dict[str, dict[str, Any]]
):
    """Read Unicode source as data and write a UTF-8 report.

    Arguments:
        tmp_path: temporary source and report directory
        audits: loaded standalone audit helpers
    """
    source = tmp_path / "unicode.py"
    source.write_text(
        'def κ():\n    return "🦊"\nraise RuntimeError("do not execute")\n',
        encoding="utf-8",
    )
    report = tmp_path / "notes.md"

    audits["audit-style"]["main"](["--target", str(source), "--output", str(report)])

    assert "κ" in report.read_text(encoding="utf-8")


@pytest.mark.parametrize("kind", ["missing", "non-python"])
def test_style_audit_rejects_invalid_targets(
    tmp_path: Path, audits: dict[str, dict[str, Any]], kind: str
):
    """Reject invalid scope without replacing an earlier report with zero findings.

    Arguments:
        tmp_path: temporary source and report directory
        audits: loaded standalone audit helpers
        kind: invalid target type
    """
    target = tmp_path / "missing"
    if kind == "non-python":
        target = tmp_path / "notes.txt"
        target.write_text("not Python", encoding="utf-8")
    report = tmp_path / "report.md"
    report.write_text("earlier report", encoding="utf-8")

    with pytest.raises(SystemExit, match="Audit target"):
        audits["audit-style"]["main"](
            ["--target", str(target), "--output", str(report)]
        )

    assert report.read_text(encoding="utf-8") == "earlier report"


def test_hierarchy_import_aliases_and_cycles(
    tmp_path: Path, audits: dict[str, dict[str, Any]]
):
    """Include every imported sibling and retain cycle diagnostics.

    Arguments:
        tmp_path: temporary package parent
        audits: loaded standalone audit helpers
    """
    package = _package(
        tmp_path,
        {
            "alpha.py": "from . import beta, gamma\n",
            "beta.py": "from example import alpha\n",
            "gamma.py": 'raise RuntimeError("do not execute")\n',
        },
    )
    audit = audits["audit-module-hierarchy"]

    edges = audit["get_sibling_import_edges"](
        package, "example", ["alpha", "beta", "gamma"]
    )
    result = audit["audit_one_package"](package, "example")

    assert edges == {"alpha": {"beta", "gamma"}, "beta": {"alpha"}, "gamma": set()}
    assert result.cycles == [["alpha", "beta"]]
    assert result.levels == {1: [["gamma"]], 2: [["alpha", "beta"]]}


@pytest.mark.parametrize(
    ("statement", "expected"),
    [
        ("from .beta import value", set()),
        ("from ..beta import value", {"beta"}),
        ("from example.beta import value", {"beta"}),
        ("import example.beta", {"beta"}),
    ],
)
def test_hierarchy_relative_import_context(
    tmp_path: Path,
    audits: dict[str, dict[str, Any]],
    statement: str,
    expected: set[str],
):
    """Distinguish imports within a child package from imports of root siblings.

    Arguments:
        tmp_path: temporary package parent
        audits: loaded standalone audit helpers
        statement: import statement in a child package module
        expected: actual root-sibling dependencies
    """
    package = _package(
        tmp_path,
        {
            "alpha/__init__.py": "",
            "alpha/consumer.py": f"{statement}\n",
            "alpha/beta.py": "value = 1\n",
            "beta.py": "value = 2\n",
        },
    )

    edges = audits["audit-module-hierarchy"]["get_sibling_import_edges"](
        package, "example", ["alpha", "beta"]
    )

    assert edges == {"alpha": expected, "beta": set()}


def test_hierarchy_nested_target_keeps_qualified_imports(
    tmp_path: Path,
    audits: dict[str, dict[str, Any]],
    capsys: pytest.CaptureFixture[str],
):
    """Detect the same cycle when auditing a nested package as the root target.

    Arguments:
        tmp_path: temporary package parent
        audits: loaded standalone audit helpers
        capsys: captured command output
    """
    package = _package(
        tmp_path,
        {
            "core/__init__.py": "",
            "core/alpha.py": "from example.core import beta\n",
            "core/beta.py": 'from . import alpha\nlabel = "🦊"\n',
        },
    )
    audit = audits["audit-module-hierarchy"]

    audit["main"](["--target", str(package / "core")])

    assert "CYCLES: alpha / beta" in capsys.readouterr().out


@pytest.mark.parametrize("bad_file", ["alpha.py", "__init__.py"])
def test_hierarchy_rejects_unparseable_source(
    tmp_path: Path, audits: dict[str, dict[str, Any]], bad_file: str
):
    """Do not hide missing dependency evidence when Python parsing fails.

    Arguments:
        tmp_path: temporary package parent
        audits: loaded standalone audit helpers
        bad_file: source file with invalid Python
    """
    package = _package(tmp_path, {"alpha.py": "", "beta.py": ""})
    (package / bad_file).write_text("def broken(\n", encoding="utf-8")

    with pytest.raises(SystemExit, match="Cannot parse Python source"):
        audits["audit-module-hierarchy"]["main"](["--target", str(package)])


@pytest.mark.parametrize("minimum", [0, -1])
def test_hierarchy_rejects_invalid_minimum(
    audits: dict[str, dict[str, Any]], minimum: int
):
    """Reject a minimum child count that cannot describe an audit scope.

    Arguments:
        audits: loaded standalone audit helpers
        minimum: invalid minimum child count
    """
    with pytest.raises(SystemExit) as exc_info:
        audits["audit-module-hierarchy"]["main"](["--min-children", str(minimum)])

    assert exc_info.value.code == 2


def test_hierarchy_rejects_missing_target(
    tmp_path: Path, audits: dict[str, dict[str, Any]]
):
    """Reject a missing package rather than completing an empty scan.

    Arguments:
        tmp_path: temporary package parent
        audits: loaded standalone audit helpers
    """
    with pytest.raises(SystemExit, match="Target package directory not found"):
        audits["audit-module-hierarchy"]["main"](
            ["--target", str(tmp_path / "missing")]
        )


def _package(tmp_path: Path, files: dict[str, str]) -> Path:
    """Create a small package whose source is never imported by the audit.

    Arguments:
        tmp_path: temporary package parent
        files: relative source paths and contents
    Returns:
        created root package
    """
    package = tmp_path / "example"
    package.mkdir()
    (package / "__init__.py").write_text("", encoding="utf-8")
    for name, source in files.items():
        path = package / name
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(source, encoding="utf-8")
    return package
