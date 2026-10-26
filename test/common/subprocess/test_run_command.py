#  Copyright 2017-2026 Karl T Debiec. All rights reserved. This software may be modified
#  and distributed under the terms of the BSD license. See the LICENSE file for details.
"""Tests of common.subprocess.run_command."""

from __future__ import annotations

import os
import sys
from pathlib import Path
from time import monotonic

from pytest import raises

from pipescaler.common.subprocess import run_command
from test.common.subprocess_cases import SUBPROCESS_SUCCESS_CASES
from test.helpers import parametrize


@parametrize(
    ("command", "expected_stdout_fragments"),
    [(command, fragments) for _, command, fragments in SUBPROCESS_SUCCESS_CASES],
    ids=[name for name, _, _ in SUBPROCESS_SUCCESS_CASES],
)
def test_run_command_success_cases(
    command: list[str], expected_stdout_fragments: tuple[str, ...]
):
    """Test running successful commands.

    Arguments:
        command: command to run
        expected_stdout_fragments: expected stdout fragments
    """
    exitcode, stdout, stderr = run_command(command)

    assert exitcode == 0
    assert stderr == ""
    if not expected_stdout_fragments:
        assert stdout == ""
    for fragment in expected_stdout_fragments:
        assert fragment in stdout


def test_run_command_with_stderr():
    """Test running a command that writes to stderr."""
    # Use Python to write to stderr.
    exitcode, stdout, stderr = run_command(
        [sys.executable, "-c", "import sys; sys.stderr.write('error message')"],
        acceptable_exitcodes=[0],
    )

    assert exitcode == 0
    assert "error message" in stderr


def test_run_command_failure_default():
    """Test running a command that fails with default acceptable exitcodes."""
    with raises(ValueError, match="failed with exit code"):
        run_command([sys.executable, "-c", "import sys; sys.exit(1)"])


def test_run_command_failure_custom_acceptable():
    """Test running a command with custom acceptable exitcodes."""
    exitcode, stdout, stderr = run_command(
        [sys.executable, "-c", "import sys; sys.exit(42)"], acceptable_exitcodes=[42]
    )

    assert exitcode == 42


def test_run_command_with_cwd_path(tmp_path: Path):
    """Test running a command with a working directory.

    Arguments:
        tmp_path: temporary directory provided by pytest
    """
    exitcode, stdout, stderr = run_command(
        [sys.executable, "-c", "from pathlib import Path; print(Path.cwd())"],
        cwd_path=tmp_path,
    )

    assert exitcode == 0
    assert stdout.strip() == str(tmp_path)
    assert stderr == ""


def test_run_command_with_env():
    """Test running a command with environment variables."""
    env = os.environ.copy()
    env["PIPESCALER_TEST_RUN_COMMAND_ENV"] = "expected"

    exitcode, stdout, stderr = run_command(
        [
            sys.executable,
            "-c",
            "import os; print(os.environ['PIPESCALER_TEST_RUN_COMMAND_ENV'])",
        ],
        env=env,
    )

    assert exitcode == 0
    assert stdout.strip() == "expected"
    assert stderr == ""


def test_run_command_timeout():
    """Test command timeout behavior."""
    start_time = monotonic()
    exitcode, stdout, stderr = run_command(
        [sys.executable, "-c", "import time; time.sleep(10)"],
        timeout=0,
        acceptable_exitcodes=[-9, -15, 1],
    )
    elapsed = monotonic() - start_time

    assert exitcode != 0
    assert elapsed < 1.0


def test_run_command_timeout_kills_descendant_holding_pipes():
    """Ensure timeout cleanup closes pipes held open by a descendant."""
    descendant_code = "import time; time.sleep(3)"
    command_code = (
        "import subprocess, sys, time; print('started', flush=True); "
        f"subprocess.Popen([sys.executable, '-c', {descendant_code!r}]); "
        "time.sleep(10)"
    )
    start_time = monotonic()

    exitcode, stdout, stderr = run_command(
        [sys.executable, "-c", command_code], timeout=0.3, acceptable_exitcodes=[-9, 1]
    )

    assert exitcode != 0
    assert "started" in stdout
    assert stderr == ""
    assert monotonic() - start_time < 2.0


def test_run_command_timeout_bounds_cleanup_when_descendant_escapes_tree(monkeypatch):
    """Bound fallback cleanup when a descendant retains the pipes.

    Arguments:
        monkeypatch: pytest monkeypatch fixture
    """
    descendant_code = "import time; time.sleep(3)"
    command_code = (
        "import subprocess, sys, time; print('started', flush=True); "
        f"subprocess.Popen([sys.executable, '-c', {descendant_code!r}]); "
        "time.sleep(10)"
    )
    monkeypatch.setattr(
        "pipescaler.common.subprocess._kill_process_tree", lambda child: child.kill()
    )
    start_time = monotonic()

    exitcode, stdout, stderr = run_command(
        [sys.executable, "-c", command_code], timeout=1.0, acceptable_exitcodes=[-9, 1]
    )

    assert exitcode != 0
    assert "started" in stdout
    assert stderr == ""
    assert monotonic() - start_time < 2.8


def test_run_command_unicode_output():
    """Test handling of Unicode output."""
    env = os.environ.copy()
    env["PYTHONIOENCODING"] = "utf-8"

    exitcode, stdout, stderr = run_command(
        [sys.executable, "-c", "print('Hello 世界')"], env=env
    )

    assert exitcode == 0
    assert "Hello" in stdout
