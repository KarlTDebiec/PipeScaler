#  Copyright 2017-2026 Karl T Debiec. All rights reserved. This software may be modified
#  and distributed under the terms of the BSD license. See the LICENSE file for details.
"""Shared subprocess command test cases."""

from __future__ import annotations

import sys

from pipescaler.common.testing import echo_command

__all__ = ["SUBPROCESS_SUCCESS_CASES"]

SUBPROCESS_SUCCESS_CASES: list[tuple[str, list[str], str]] = [
    (
        "literal-arguments",
        echo_command(
            "arg1",
            "hello world",
            "$HOME",
            "$(whoami)",
            "; ls",
            "test; rm -rf /",
            "test | cat /etc/passwd",
            "`whoami`",
            "'single quotes'",
            '"double quotes"',
        ),
        "arg1 hello world $HOME $(whoami) ; ls test; rm -rf / "
        "test | cat /etc/passwd `whoami` 'single quotes' \"double quotes\"\n",
    ),
    (
        "multiple-lines",
        [sys.executable, "-c", "print('line1'); print('line2')"],
        "line1\nline2\n",
    ),
    ("empty-output", [sys.executable, "-c", ""], ""),
]
