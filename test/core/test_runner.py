#  Copyright 2020-2026 Karl T Debiec. All rights reserved. This software may be modified
#  and distributed under the terms of the BSD license. See the LICENSE file for details.
"""Tests for executable runner argument handling."""

from __future__ import annotations

import json
import sys
from pathlib import Path
from typing import Any

import pytest

from pipescaler.core.runner import Runner


class _ArgumentRecorder(Runner):
    """Run Python to record its received arguments without external dependencies."""

    def get_command(self, input_path: Path | str, output_path: Path | str) -> list[str]:
        """Build a command that records the input path and custom arguments.

        Arguments:
            input_path: input path to pass through unchanged
            output_path: JSON file in which to record received arguments
        Returns:
            Python executable and individual argument tokens
        """
        return [
            str(self.executable_path),
            "-c",
            "import json, sys; from pathlib import Path; "
            "Path(sys.argv[2]).write_text(json.dumps(sys.argv[1:]), encoding='utf-8')",
            str(input_path),
            str(output_path),
            *self.arguments,
        ]

    @classmethod
    def executable(cls) -> str:
        """Return the current Python interpreter.

        Returns:
            path of the interpreter running this test
        """
        return sys.executable


def test_subprocess_receives_literal_tokens(tmp_path: Path):
    """Preserve shell metacharacters, whitespace, Unicode, and empty arguments.

    Arguments:
        tmp_path: temporary test directory
    """
    input_path = r"C:\input images\O'Brien\{source}.png"
    output_path = tmp_path / "O'Brien {output} 日本語.json"
    arguments = ["C:\\custom options\\folder\\", "", 'a"b', "${value}", "one two"]
    runner = _ArgumentRecorder(arguments=arguments)
    arguments.append("not part of the runner")

    runner(input_path, output_path)

    assert json.loads(output_path.read_text(encoding="utf-8")) == [
        input_path,
        str(output_path),
        "C:\\custom options\\folder\\",
        "",
        'a"b',
        "${value}",
        "one two",
    ]


@pytest.mark.parametrize("arguments", ["--option value", ["--option", 1]])
def test_arguments_require_string_tokens(arguments: Any):
    """Reject command strings and invalid token types instead of guessing syntax.

    Arguments:
        arguments: invalid argument value to reject
    """
    with pytest.raises(TypeError, match="sequence of individual string tokens"):
        _ArgumentRecorder(arguments=arguments)
