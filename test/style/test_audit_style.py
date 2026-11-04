#  Copyright 2026 Karl T Debiec. All rights reserved. This software may be modified
#  and distributed under the terms of the BSD license. See the LICENSE file for details.
"""Behavioral regression coverage for advisory style audit reports."""

from __future__ import annotations

from pathlib import Path
from subprocess import run
from sys import executable

import pytest

from pipescaler.common import package_root


@pytest.mark.parametrize(
    "header",
    [
        "#  Copyright 2026- Karl T Debiec. All rights reserved. "
        "This software may be modified\n"
        "#  and distributed under the terms of the BSD license. "
        "See the LICENSE file for details.",
        "#  Copyright 2026 Karl T Debiec. All rights reserved. "
        "This software may be modified\n#  Missing BSD license notice.",
        "#  Copyright 2026 Karl T Debiec. All rights reserved. "
        "This software may be modified",
    ],
    ids=["incomplete-year-range", "wrong-license-text", "missing-license-line"],
)
def test_malformed_headers_produce_copyright_notes(tmp_path: Path, header: str):
    """Report a malformed year or missing standard license text at the first line.

    Arguments:
        tmp_path: temporary source and report directory
        header: incomplete or malformed copyright and license header
    """
    source_path = tmp_path / "example.py"
    source_path.write_text(f'{header}\n"""Example source."""\n', encoding="utf-8")
    report_path = tmp_path / "report.md"
    result = run(
        [
            executable,
            str(
                package_root.parent
                / ".agents/skills/audit-style/scripts/audit_style.py"
            ),
            "--target",
            str(source_path),
            "--output",
            str(report_path),
        ],
        capture_output=True,
        text=True,
        encoding="utf-8",
        timeout=10,
        check=False,
    )

    assert result.returncode == 0, result.stderr
    report = report_path.read_text(encoding="utf-8")
    assert "- Total notes: 1" in report
    assert (
        "Line 1: **Copyright** - missing or nonstandard two-line copyright header"
        in report
    )


@pytest.mark.parametrize(
    "years", ["2026", "2017-2026", "2020-2026", "2019-2025", "2027"]
)
def test_standard_header_years_produce_no_copyright_notes(tmp_path: Path, years: str):
    """Accept standard single years and ranges without rewriting their dates.

    Arguments:
        tmp_path: temporary source and report directory
        years: established copyright year or range
    """
    source_path = tmp_path / "example.py"
    source = (
        f"#  Copyright {years} Karl T Debiec. All rights reserved. "
        "This software may be modified\n"
        "#  and distributed under the terms of the BSD license. "
        "See the LICENSE file for details.\n"
        '"""Example source."""\n'
    )
    source_path.write_text(source, encoding="utf-8")
    report_path = tmp_path / "report.md"
    result = run(
        [
            executable,
            str(
                package_root.parent
                / ".agents/skills/audit-style/scripts/audit_style.py"
            ),
            "--target",
            str(source_path),
            "--output",
            str(report_path),
        ],
        capture_output=True,
        text=True,
        encoding="utf-8",
        timeout=10,
        check=False,
    )

    assert result.returncode == 0, result.stderr
    assert "- Total notes: 0" in report_path.read_text(encoding="utf-8")
    assert source_path.read_text(encoding="utf-8") == source
