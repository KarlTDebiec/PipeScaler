#  Copyright 2017-2026 Karl T Debiec. All rights reserved. This software may be modified
#  and distributed under the terms of the BSD license. See the LICENSE file for details.
"""Tests of common.subprocess.run_command."""

from __future__ import annotations

import os
import sys
from collections.abc import Callable
from contextlib import nullcontext
from pathlib import Path
from subprocess import Popen, TimeoutExpired
from threading import enumerate as enumerate_threads
from time import monotonic, sleep

from pytest import FixtureRequest, MonkeyPatch, fixture, raises

from pipescaler.common import subprocess as subprocess_module
from pipescaler.common.subprocess import run_command, run_command_live
from test.common.subprocess_cases import SUBPROCESS_SUCCESS_CASES
from test.helpers import parametrize


@fixture(params=[run_command, run_command_live], ids=["capture", "live"])
def run(request: FixtureRequest) -> Callable[..., tuple[int, str, str]]:
    """Provide each public subprocess interface for the shared contract checks.

    Arguments:
        request: parametrized subprocess function
    Returns:
        subprocess function under test
    """
    return request.param


@parametrize(
    ("command", "expected_stdout"),
    [(command, expected) for _, command, expected in SUBPROCESS_SUCCESS_CASES],
    ids=[name for name, _, _ in SUBPROCESS_SUCCESS_CASES],
)
def test_run_command_success_cases(
    run: Callable[..., tuple[int, str, str]],
    command: list[str],
    expected_stdout: str,
):
    """Preserve literal arguments, multiple lines, and empty output.

    Arguments:
        run: subprocess interface
        command: command to run
        expected_stdout: complete normalized output
    """
    exitcode, stdout, stderr = run(command)
    assert exitcode == 0
    assert stderr == ""
    assert stdout.replace("\r\n", "\n") == expected_stdout


def test_run_command_with_stderr(run: Callable[..., tuple[int, str, str]]):
    """Capture the child's standard error separately from standard output.

    Arguments:
        run: subprocess interface
    """
    exitcode, stdout, stderr = run(
        [sys.executable, "-c", "import sys; sys.stderr.write('error message')"],
        acceptable_exitcodes=[0],
    )

    assert exitcode == 0
    assert stdout == ""
    assert stderr == "error message"


@parametrize(
    "code, acceptable, error",
    [(0, None, None), (1, None, ValueError), (42, [42], None)],
)
def test_exit_codes(
    run: Callable[..., tuple[int, str, str]],
    code: int,
    acceptable: list[int] | None,
    error: type[Exception] | None,
):
    """Reject failures unless the caller explicitly accepts their exit status.

    Arguments:
        run: subprocess interface
        code: child exit status
        acceptable: accepted statuses, or none for defaults
        error: expected exception, or none for success
    """
    options = {} if acceptable is None else {"acceptable_exitcodes": acceptable}
    with raises(error, match="failed with exit code") if error else nullcontext():
        assert run(
            [sys.executable, "-c", f"import sys; sys.exit({code})"], **options
        ) == (code, "", "")


def test_run_command_with_cwd_path(
    run: Callable[..., tuple[int, str, str]], tmp_path: Path
):
    """Test running a command with a working directory.

    Arguments:
        run: subprocess interface
        tmp_path: temporary directory provided by pytest
    """
    exitcode, stdout, stderr = run(
        [sys.executable, "-c", "from pathlib import Path; print(Path.cwd())"],
        cwd_path=tmp_path,
    )

    assert exitcode == 0
    assert stdout.strip() == str(tmp_path)
    assert stderr == ""


def test_run_command_with_env(run: Callable[..., tuple[int, str, str]]):
    """Test running a command with environment variables.

    Arguments:
        run: subprocess interface
    """
    env = os.environ.copy()
    env["PIPESCALER_TEST_RUN_COMMAND_ENV"] = "expected"

    exitcode, stdout, stderr = run(
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


@parametrize(
    "payload, expected", [("Hello 世界".encode(), "Hello 世界"), (b"\xff", "ÿ")]
)
def test_output_decoding(
    run: Callable[..., tuple[int, str, str]],
    payload: bytes,
    expected: str,
):
    """Decode Unicode and fallback byte encodings without losing characters.

    Arguments:
        run: subprocess interface
        payload: child output bytes
        expected: decoded output
    """
    assert run(
        [sys.executable, "-c", f"import sys; sys.stdout.buffer.write({payload!r})"]
    ) == (0, expected, "")


def test_live_timeout():
    """Raise a timeout from the streaming interface without waiting for the child."""
    start_time = monotonic()
    with raises(TimeoutExpired):
        run_command_live(
            [sys.executable, "-c", "import time; time.sleep(2)"], timeout=0
        )
    assert monotonic() - start_time < 1.0


@parametrize(
    ("live", "parent_exits", "kill_tree"),
    [
        (False, False, True),
        (False, True, True),
        (True, False, True),
        (True, True, True),
        (False, True, False),
        (True, True, False),
    ],
)
def test_timeout_cleans_up_inherited_pipes(
    live: bool,
    parent_exits: bool,
    kill_tree: bool,
    tmp_path: Path,
    monkeypatch: MonkeyPatch,
):
    """Terminate descendants and bound readers even when tree cleanup misses them.

    Arguments:
        live: whether to use the live logging helper
        parent_exits: whether the direct child exits before the command deadline
        kill_tree: whether process-tree cleanup is allowed to terminate descendants
        tmp_path: directory for the descendant heartbeat
        monkeypatch: fixture for simulating an escaped descendant
    """
    if not kill_tree:

        def kill_direct_child(child: Popen[bytes], job: object):
            """Simulate tree cleanup missing descendants.

            Arguments:
                child: direct child to reap
                job: unused process-tree ownership
            """
            if child.poll() is None:
                child.kill()
            child.wait(timeout=1)

        monkeypatch.setattr(
            subprocess_module, "_terminate_process_tree", kill_direct_child
        )
    heartbeat_path = tmp_path / "heartbeat.txt"
    descendant_code = (
        "import sys, time\nfrom pathlib import Path\n"
        "print('descendant output', flush=True)\n"
        "print('descendant error', file=sys.stderr, flush=True)\n"
        f"heartbeat = Path({str(heartbeat_path)!r})\n"
        "heartbeat.write_text('0')\n"
        "for i in range(1, 61):\n"
        " with heartbeat.open('a') as stream:\n  stream.write(str(i) + '\\n')\n"
        " time.sleep(0.05)\n"
    )
    parent_code = (
        "import subprocess, sys, time\nfrom pathlib import Path\n"
        f"subprocess.Popen([sys.executable, '-c', {descendant_code!r}])\n"
        f"heartbeat = Path({str(heartbeat_path)!r})\n"
        "while not heartbeat.exists():\n    time.sleep(0.01)\n"
        "print('parent ready', flush=True)\n"
    )
    if not parent_exits:
        parent_code += "time.sleep(10)"
    command = [sys.executable, "-c", parent_code]
    start_time = monotonic()
    if live:
        with raises(TimeoutExpired) as exc:
            run_command_live(command, timeout=1.0)
        stdout = exc.value.output
        stderr = exc.value.stderr
    else:
        exitcode, stdout, stderr = run_command(
            command, timeout=1.0, acceptable_exitcodes=[0, -9, 1]
        )
        if parent_exits:
            assert exitcode == 0
        else:
            assert exitcode != 0
    assert monotonic() - start_time < 2.0
    assert isinstance(stdout, str)
    assert isinstance(stderr, str)
    assert "parent ready" in stdout
    assert "descendant output" in stdout
    assert "descendant error" in stderr
    assert heartbeat_path.exists()
    assert not any(
        thread.name.startswith("pipescaler-reader-") for thread in enumerate_threads()
    )
    sleep(0.1)
    heartbeat = heartbeat_path.read_text()
    sleep(0.2)
    if kill_tree:
        assert heartbeat_path.read_text() == heartbeat
    else:
        assert heartbeat_path.read_text() != heartbeat


@parametrize("live", [False, True])
def test_capture_preserves_complete_output(live: bool):
    """Capture both streams beyond pipe-buffer sizes without truncation.

    Arguments:
        live: whether to use live logging with its deadline disabled
    """
    command = [
        sys.executable,
        "-c",
        "import sys; sys.stdout.write('x' * 131072); sys.stderr.write('y' * 131072)",
    ]
    if live:
        exitcode, stdout, stderr = run_command_live(command, timeout=None)
    else:
        exitcode, stdout, stderr = run_command(command, timeout=5)
    assert exitcode == 0
    assert stdout == "x" * 131072
    assert stderr == "y" * 131072
