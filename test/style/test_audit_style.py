#  Copyright 2020-2026 Karl T Debiec. All rights reserved. This software may be modified
#  and distributed under the terms of the BSD license. See the LICENSE file for details.
"""Regression coverage for the advisory style audit."""

from __future__ import annotations

from pathlib import Path
from runpy import run_path

import pytest


def test_audit_report_limits_zero_notes(tmp_path: Path):
    """Test an empty report describes the limits of its evidence.

    Arguments:
        tmp_path: temporary directory path
    """
    audit = run_path(
        str(Path(__file__).parents[2] / "skills/audit-style/scripts/audit_style.py")
    )
    report_path = tmp_path / "notes.md"
    audit["write_report"]([], {}, report_path)
    report = report_path.read_text()
    assert "Total notes: 0" in report
    assert "not proof of compliance" in report
    assert "was sampled" not in report


@pytest.mark.parametrize(
    ("source", "expected"),
    [
        ("def _helper(): pass\ndef public(): pass", ["public"]),
        ("def zebra(): pass\nasync def alpha(): pass", ["alpha"]),
        ("@cache\ndef alpha(): pass\ndef zebra(): pass", ["zebra"]),
        (
            "class Sample:\n def __repr__(self): pass\n def __call__(self): pass",
            ["__call__"],
        ),
        (
            "class Sample:\n"
            " def observe(self): pass\n"
            " def checkpoints_current(self): pass",
            ["checkpoints_current"],
        ),
        (
            "class Sample:\n"
            " @staticmethod\n"
            " def alpha(): pass\n"
            " @classmethod\n"
            " def zebra(cls): pass",
            ["zebra"],
        ),
        (
            "class Sample:\n"
            " def method(self): pass\n"
            " @property\n"
            " def value(self): pass",
            ["value"],
        ),
        (
            "class Sample:\n"
            " @property\n"
            " def alpha(self): pass\n"
            " @alpha.setter\n"
            " def alpha(self, value): pass\n"
            " @property\n"
            " def zebra(self): pass",
            [],
        ),
        (
            "@overload\n"
            "def zebra(): pass\n"
            "@overload\n"
            "def zebra(value): pass\n"
            "def alpha(): pass\n"
            "def zebra(): pass",
            [],
        ),
        ("class Sample:\n @custom\n def zebra(self): pass\n def alpha(self): pass", []),
        ("if enabled:\n def zebra(): pass\n def alpha(): pass", []),
        (
            "class Sample:\n"
            " def __init__(self): pass\n"
            " def __call__(self): pass\n"
            " @property\n"
            " def alpha(self): pass\n"
            " def method(self): pass\n"
            " @classmethod\n"
            " def build(cls): pass\n"
            " @staticmethod\n"
            " def create(): pass\n"
            " @property\n"
            " def _value(self): pass\n"
            " def _helper(self): pass",
            [],
        ),
    ],
)
def test_audit_definition_order(tmp_path: Path, source: str, expected: list[str]):
    """Test ordering notes cover clear groups and omit ambiguous definitions.

    Arguments:
        tmp_path: temporary directory path
        source: sample module source
        expected: names reported as out of order
    """
    messages = _audit(tmp_path, source, "Ordering")
    assert [message.split("`")[1] for message in messages] == expected


@pytest.mark.parametrize(
    ("section", "description", "expected"),
    [
        ("Arguments", "value: The input value", True),
        ("Arguments", "value:\n            Whether to proceed", True),
        ("Returns", "The result", True),
        ("Yields", "An item", True),
        ("Returns", "the result", False),
        ("Returns", "Path to the result", False),
        ("Returns", "Widget instance", False),
        ("Arguments", "value: input value\n            The continuation", False),
        ("Raises", "ValueError: The input is invalid", False),
    ],
)
def test_audit_description_case(
    tmp_path: Path, section: str, description: str, expected: bool
):
    """Test common capitalized prose is detected without rejecting type names.

    Arguments:
        tmp_path: temporary directory path
        section: docstring section name
        description: section contents
        expected: whether the audit reports capitalization
    """
    source = (
        f'\ndef sample(value):\n    """Sample.\n\n    {section}:\n'
        f'        {description}\n    """\n    pass\n'
    )
    messages = _audit(tmp_path, source, "Documentation")
    assert (
        bool([message for message in messages if "description begins" in message])
        == expected
    )


@pytest.mark.parametrize(
    ("source", "expected"),
    [
        (
            '__all__ = ["Thing"]\nclass Thing: pass\ntype ModeSetting = str | int',
            ["ModeSetting"],
        ),
        (
            '__all__ = ["Thing"]\n'
            "class Thing: pass\n"
            "ModeSetting: TypeAlias = str | int",
            ["ModeSetting"],
        ),
        ('__all__ = ["Thing"]\nclass Thing: pass\ndef public(): pass', ["public"]),
        (
            '__all__ = ["Thing"]\nclass Thing: pass\nasync def public(): pass',
            ["public"],
        ),
        (
            '__all__ = ["Thing", "ModeSetting"]\n'
            "class Thing: pass\n"
            "type ModeSetting = str",
            [],
        ),
        (
            '__all__ = ["Thing"]\n'
            "class Thing: pass\n"
            "CONSTANT = 1\n"
            "from other import Alias\n"
            "def _private(): pass",
            [],
        ),
        ('__all__ = ["Thing"]\n__all__ += ["public"]\ndef public(): pass', []),
        ('__all__ = ["Thing"]\n__all__.append("public")\ndef public(): pass', []),
        ("__all__ = [*names]\ndef public(): pass", []),
        ("__all__ = names\ndef public(): pass", []),
        ('__all__ = ["Thing"]\n__all__ = ["public"]\ndef public(): pass', []),
        ('__all__ = ["Thing"]\nclass Thing:\n def method(self): pass', []),
    ],
)
def test_audit_export_membership(tmp_path: Path, source: str, expected: list[str]):
    """Test literal exports cover definitions without guessing dynamic intent.

    Arguments:
        tmp_path: temporary directory path
        source: sample module source
        expected: declarations missing from exports
    """
    messages = _audit(tmp_path, source, "Exports")
    assert messages == [
        f"public declaration `{name}` is missing from `__all__`" for name in expected
    ]


def _audit(tmp_path: Path, source: str, category: str) -> list[str]:
    """Run the audit against a source sample and select one note category.

    Arguments:
        tmp_path: temporary directory path
        source: sample module source
        category: note category to select
    Returns:
        matching note messages
    """
    audit = run_path(
        str(Path(__file__).parents[2] / "skills/audit-style/scripts/audit_style.py")
    )
    source_path = tmp_path / "sample.py"
    source_path.write_text(source)
    _, notes = audit["audit_paths"](source_path)
    return [
        note.message
        for note in notes.get(source_path.as_posix(), [])
        if note.category == category
    ]
