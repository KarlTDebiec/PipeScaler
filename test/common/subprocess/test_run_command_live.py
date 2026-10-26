#  Copyright 2017-2026 Karl T Debiec. All rights reserved. This software may be modified
#  and distributed under the terms of the BSD license. See the LICENSE file for details.
"""Tests of common.subprocess.run_command_live."""

from __future__ import annotations

import os
import sys
from pathlib import Path
from subprocess import TimeoutExpired
from threading import enumerate as enumerate_threads
from time import monotonic, sleep
from unittest.mock import Mock

from pytest import raises

from pipescaler.common import subprocess as subprocess_module
from pipescaler.common.subprocess import run_command_live
from test.common.subprocess_cases import SUBPROCESS_SUCCESS_CASES
from test.helpers import parametrize


@parametrize(
    ("command", "expected_stdout_fragments"),
    [(command, fragments) for _, command, fragments in SUBPROCESS_SUCCESS_CASES],
    ids=[name for name, _, _ in SUBPROCESS_SUCCESS_CASES],
)
def test_run_command_live_success_cases(
    command: list[str], expected_stdout_fragments: tuple[str, ...]
):
    """Test running successful commands with live output.

    Arguments:
        command: command to run
        expected_stdout_fragments: expected stdout fragments
    """
    exitcode, stdout, stderr = run_command_live(command)

    assert exitcode == 0
    assert stderr == ""
    if not expected_stdout_fragments:
        assert stdout == ""
    for fragment in expected_stdout_fragments:
        assert fragment in stdout


def test_run_command_live_with_stderr():
    """Test running a command with live stderr output."""
    exitcode, stdout, stderr = run_command_live(
        [sys.executable, "-c", "import sys; sys.stderr.write('error message')"],
        acceptable_exitcodes=[0],
    )

    assert exitcode == 0
    assert "error message" in stderr


def test_run_command_live_failure_default():
    """Test running a command that fails with default acceptable exitcodes."""
    with raises(ValueError, match="failed with exit code"):
        run_command_live([sys.executable, "-c", "import sys; sys.exit(1)"])


def test_run_command_live_failure_custom_acceptable():
    """Test running a command with custom acceptable exitcodes."""
    exitcode, stdout, stderr = run_command_live(
        [sys.executable, "-c", "import sys; sys.exit(42)"], acceptable_exitcodes=[42]
    )

    assert exitcode == 42


def test_run_command_live_with_cwd_path(tmp_path: Path):
    """Test running a live command with a working directory.

    Arguments:
        tmp_path: temporary directory provided by pytest
    """
    exitcode, stdout, stderr = run_command_live(
        [sys.executable, "-c", "from pathlib import Path; print(Path.cwd())"],
        cwd_path=tmp_path,
    )

    assert exitcode == 0
    assert stdout.strip() == str(tmp_path)
    assert stderr == ""


def test_run_command_live_with_env():
    """Test running a live command with environment variables."""
    env = os.environ.copy()
    env["PIPESCALER_TEST_RUN_COMMAND_LIVE_ENV"] = "expected"

    exitcode, stdout, stderr = run_command_live(
        [
            sys.executable,
            "-c",
            "import os; print(os.environ['PIPESCALER_TEST_RUN_COMMAND_LIVE_ENV'])",
        ],
        env=env,
    )

    assert exitcode == 0
    assert stdout.strip() == "expected"
    assert stderr == ""


def test_run_command_live_timeout():
    """Test command timeout behavior."""
    start_time = monotonic()
    with raises(TimeoutExpired):
        run_command_live(
            [sys.executable, "-c", "import time; time.sleep(2)"], timeout=0
        )
    elapsed = monotonic() - start_time

    assert elapsed < 1.0


def test_run_command_live_timeout_kills_descendant_holding_pipes():
    """Ensure timeout cleanup closes pipes held open by a descendant."""
    descendant_code = "import time; time.sleep(3)"
    command_code = (
        "import subprocess, sys, time; print('started', flush=True); "
        f"subprocess.Popen([sys.executable, '-c', {descendant_code!r}]); "
        "time.sleep(10)"
    )
    start_time = monotonic()

    with raises(TimeoutExpired) as exception_info:
        run_command_live([sys.executable, "-c", command_code], timeout=0.3)

    assert "started" in exception_info.value.output
    assert monotonic() - start_time < 2.0


def test_run_command_live_timeout_bounds_cleanup_when_descendant_escapes_tree(
    monkeypatch,
):
    """Bound reader cleanup when a descendant retains the pipes.

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
        subprocess_module, "_kill_process_tree", lambda child: child.kill()
    )
    start_time = monotonic()

    with raises(TimeoutExpired) as exception_info:
        run_command_live([sys.executable, "-c", command_code], timeout=0.3)

    assert "started" in exception_info.value.output
    assert monotonic() - start_time < 2.8


def test_run_command_live_timeout_stops_readers_while_descendant_runs(
    monkeypatch, tmp_path: Path
):
    """Stop reader threads even while an escaped descendant remains alive.

    Arguments:
        monkeypatch: pytest monkeypatch fixture
        tmp_path: temporary directory provided by pytest
    """
    alive_path = tmp_path / "descendant-alive.txt"
    done_path = tmp_path / "descendant-done.txt"
    descendant_code = (
        "from pathlib import Path; import time; "
        f"Path({str(alive_path)!r}).write_text('alive'); "
        "time.sleep(2); "
        f"Path({str(done_path)!r}).write_text('done')"
    )
    command_code = (
        "import subprocess, sys, time; print('started', flush=True); "
        f"subprocess.Popen([sys.executable, '-c', {descendant_code!r}]); "
        "time.sleep(10)"
    )
    monkeypatch.setattr(
        subprocess_module, "_kill_process_tree", lambda child: child.kill()
    )

    with raises(TimeoutExpired):
        run_command_live([sys.executable, "-c", command_code], timeout=1.0)

    assert alive_path.exists()
    assert not done_path.exists()
    assert not any(
        thread.name.startswith("pipescaler-reader-") for thread in enumerate_threads()
    )

    deadline = monotonic() + 3.0
    while not done_path.exists() and monotonic() < deadline:
        sleep(0.05)
    assert done_path.exists()


def test_run_command_live_closes_windows_job_on_success(monkeypatch):
    """Ensure successful live commands release their Windows job handle.

    Arguments:
        monkeypatch: pytest monkeypatch fixture
    """
    kernel32 = Mock()
    kernel32.CreateJobObjectW.return_value = 101
    kernel32.OpenProcess.return_value = 202
    kernel32.AssignProcessToJobObject.return_value = 1
    kernel32.CloseHandle.return_value = 1
    monkeypatch.setattr(subprocess_module, "os_name", "nt")
    monkeypatch.setattr(
        subprocess_module.ctypes,
        "WinDLL",
        lambda *args, **kwargs: kernel32,
        raising=False,
    )

    exitcode, stdout, stderr = run_command_live([sys.executable, "-c", "print('ok')"])

    assert exitcode == 0
    assert stdout.strip() == "ok"
    assert stderr == ""
    assert [call.args[0] for call in kernel32.CloseHandle.call_args_list] == [202, 101]


def test_run_command_live_closes_windows_job_on_failure(monkeypatch):
    """Ensure failing live commands release their Windows job handle.

    Arguments:
        monkeypatch: pytest monkeypatch fixture
    """
    kernel32 = Mock()
    kernel32.CreateJobObjectW.return_value = 101
    kernel32.OpenProcess.return_value = 202
    kernel32.AssignProcessToJobObject.return_value = 1
    kernel32.CloseHandle.return_value = 1
    monkeypatch.setattr(subprocess_module, "os_name", "nt")
    monkeypatch.setattr(
        subprocess_module.ctypes,
        "WinDLL",
        lambda *args, **kwargs: kernel32,
        raising=False,
    )

    with raises(ValueError, match="failed with exit code"):
        run_command_live([sys.executable, "-c", "import sys; sys.exit(1)"])

    assert [call.args[0] for call in kernel32.CloseHandle.call_args_list] == [202, 101]


def test_run_command_live_cleans_up_when_windows_job_assignment_fails(monkeypatch):
    """Ensure failed Windows job assignment releases handles and stops the child.

    Arguments:
        monkeypatch: pytest monkeypatch fixture
    """
    kernel32 = Mock()
    kernel32.CreateJobObjectW.return_value = 101
    kernel32.OpenProcess.return_value = 202
    kernel32.AssignProcessToJobObject.return_value = 0
    kernel32.CloseHandle.return_value = 1
    monkeypatch.setattr(subprocess_module, "os_name", "nt")
    monkeypatch.setattr(
        subprocess_module.ctypes,
        "WinDLL",
        lambda *args, **kwargs: kernel32,
        raising=False,
    )

    with raises(OSError, match="could not assign Windows subprocess job"):
        run_command_live(
            [sys.executable, "-c", "import time; time.sleep(10)"], timeout=10
        )

    assert [call.args[0] for call in kernel32.CloseHandle.call_args_list] == [
        202,
        101,
    ]


def test_assign_process_job_accepts_child_exiting_before_assignment(monkeypatch):
    """Accept a Windows child that exits before it can be assigned to a job.

    Arguments:
        monkeypatch: pytest monkeypatch fixture
    """
    child = Mock()
    child.pid = 123
    child.poll.return_value = 0
    kernel32 = Mock()
    kernel32.CreateJobObjectW.return_value = 101
    kernel32.OpenProcess.return_value = 0
    kernel32.CloseHandle.return_value = 1
    monkeypatch.setattr(subprocess_module, "os_name", "nt")
    monkeypatch.setattr(
        subprocess_module.ctypes,
        "WinDLL",
        lambda *args, **kwargs: kernel32,
        raising=False,
    )

    subprocess_module._assign_process_job(child)

    child.poll.assert_called_once_with()
    kernel32.CloseHandle.assert_called_once_with(101)
    assert "_pipescaler_job_handle" not in child.__dict__


def test_managed_process_closes_streams_when_assignment_fails(monkeypatch):
    """Close both owned streams when process-tree setup fails.

    Arguments:
        monkeypatch: pytest monkeypatch fixture
    Raises:
        OSError: when process-tree setup is mocked to fail
    """
    child = Mock()
    child.stdout = Mock()
    child.stderr = Mock()
    child._pipescaler_job_handle = None
    child.stdout_thread = None
    child.stderr_thread = None
    child._pipescaler_reader_threads = ()
    child._pipescaler_reader_stop_events = ()
    child.poll.return_value = None
    child.wait.return_value = -9
    monkeypatch.setattr(subprocess_module, "Popen", Mock(return_value=child))
    monkeypatch.setattr(subprocess_module.os, "set_blocking", lambda *args: None)
    monkeypatch.setattr(
        subprocess_module,
        "_assign_process_job",
        Mock(side_effect=OSError("assignment failed")),
    )
    monkeypatch.setattr(subprocess_module, "_kill_process_tree", lambda process: None)

    with raises(OSError, match="assignment failed"):
        with subprocess_module._managed_process(
            [sys.executable], cwd_path=None, env=None
        ):
            raise AssertionError("process setup should fail before yielding")

    child.stdout.close.assert_called_once_with()
    child.stderr.close.assert_called_once_with()


def test_run_command_live_non_utf8_output():
    """Test handling of non-UTF-8 output."""
    exitcode, stdout, stderr = run_command_live(
        [sys.executable, "-c", "import sys; sys.stdout.buffer.write(b'\\xff')"]
    )

    assert exitcode == 0
    assert stdout == "ÿ"
    assert stderr == ""
