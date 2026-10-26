#  Copyright 2017-2026 Karl T Debiec. All rights reserved. This software may be modified
#  and distributed under the terms of the BSD license. See the LICENSE file for details.
"""Subprocess-related utility functions."""

from __future__ import annotations

from collections.abc import Iterable, Mapping
from logging import getLogger
from os import read, set_blocking
from pathlib import Path
from subprocess import PIPE, Popen, TimeoutExpired
from threading import Event, Thread
from time import monotonic
from typing import IO

__all__ = ["run_command", "run_command_live"]

logger = getLogger(__name__)
_CLEANUP_TIMEOUT = 1.0


def run_command(
    command: list[str],
    timeout: float = 600,
    acceptable_exitcodes: Iterable[int] | None = None,
    *,
    cwd_path: Path | None = None,
    env: Mapping[str, str] | None = None,
) -> tuple[int, str, str]:
    """Run an argument list without a shell and capture its output.

    On timeout, stop the direct child and cancel output readers after bounded
    cleanup. Descendants are not terminated, and output they produce afterward is
    not captured. The resulting exit code is checked normally; the command deadline
    does not raise TimeoutExpired. Output uses UTF-8 with ISO-8859-1 fallback.

    Arguments:
        command: command to run as a list of arguments
        timeout: seconds to wait before killing the child; defaults to 600
        acceptable_exitcodes: allowed exit codes; defaults to [0]
        cwd_path: working directory; None inherits the current directory
        env: complete child environment; None inherits the current environment
    Returns:
        exitcode, standard output, and standard error
    Raises:
        OSError: if the child cannot be started
        TimeoutExpired: if cleanup cannot reap the direct child within its deadline
        ValueError: if the exit code is not accepted, including after a timeout
    """
    if acceptable_exitcodes is None:
        acceptable_exitcodes = [0]

    child = Popen(command, stdout=PIPE, stderr=PIPE, cwd=cwd_path, env=env, bufsize=0)
    stdout_str, stderr_str = _collect_output(child, timeout, live=False)
    exitcode = child.returncode

    if exitcode not in acceptable_exitcodes:
        command_str = " ".join(command)
        raise ValueError(
            f"subprocess for command:\n"
            f"{command_str}\n\n"
            f"failed with exit code {exitcode};\n\n"
            f"STDOUT:\n"
            f"{stdout_str}\n\n"
            f"STDERR:\n"
            f"{stderr_str}"
        )

    return exitcode, stdout_str, stderr_str


def run_command_live(
    command: list[str],
    timeout: float | None = 86400,
    acceptable_exitcodes: Iterable[int] | None = None,
    *,
    cwd_path: Path | None = None,
    env: Mapping[str, str] | None = None,
) -> tuple[int, str, str]:
    """Run an argument list and log both output streams at INFO level.

    Both streams are also captured and returned as text, decoded as UTF-8 with
    ISO-8859-1 fallback. Newlines and carriage returns delimit live log records.
    On timeout, stop the direct child, cancel output readers after bounded cleanup,
    and raise TimeoutExpired with captured text in output and stderr. Descendants
    are not terminated, and output they produce afterward is not captured.

    Arguments:
        command: command to run as a list of arguments
        timeout: seconds allowed for process exit and stream readers to finish;
          defaults to 86400; None disables the deadline
        acceptable_exitcodes: allowed exit codes; defaults to [0]
        cwd_path: working directory; None inherits the current directory
        env: complete child environment; None inherits the current environment
    Returns:
        exitcode, standard output, and standard error
    Raises:
        OSError: if the child cannot be started
        TimeoutExpired: if the process or its output readers exceed the deadline
        ValueError: if the exit code is not accepted
    """
    if acceptable_exitcodes is None:
        acceptable_exitcodes = [0]

    child = Popen(command, stdout=PIPE, stderr=PIPE, cwd=cwd_path, env=env, bufsize=0)
    stdout_str, stderr_str = _collect_output(child, timeout, live=True)
    exitcode = child.returncode

    if exitcode not in acceptable_exitcodes:
        command_str = " ".join(command)
        raise ValueError(
            f"subprocess for command:\n"
            f"{command_str}\n\n"
            f"failed with exit code {exitcode};\n\n"
            f"STDOUT:\n"
            f"{stdout_str}\n\n"
            f"STDERR:\n"
            f"{stderr_str}"
        )

    return exitcode, stdout_str, stderr_str


def _collect_output(
    child: Popen[bytes], timeout: float | None, *, live: bool
) -> tuple[str, str]:
    """Collect both streams within the command deadline and bound cleanup.

    Arguments:
        child: process whose output and lifetime are owned by this call
        timeout: command deadline in seconds, or None to disable it
        live: whether output records are mirrored to logs
    Returns:
        captured standard output and standard error
    Raises:
        OSError: if pipe setup or process cleanup fails
        TimeoutExpired: if a live command exceeds its deadline or cleanup cannot reap
          the direct child within the cleanup window
    """
    assert child.stdout is not None
    assert child.stderr is not None
    stdout_chunks: list[bytes] = []
    stderr_chunks: list[bytes] = []
    stop_event = Event()
    readers: list[Thread] = []
    timed_out = False
    deadline = None
    if timeout is not None:
        deadline = monotonic() + timeout
    try:
        for label, stream, chunks in (
            ("stdout", child.stdout, stdout_chunks),
            ("stderr", child.stderr, stderr_chunks),
        ):
            set_blocking(stream.fileno(), False)
            reader = Thread(
                target=_read_stream,
                args=(stream, chunks, stop_event),
                kwargs={"live": live},
                name=f"pipescaler-reader-{label}-{child.pid}",
                daemon=True,
            )
            reader.start()
            readers.append(reader)
        try:
            remaining = None
            if deadline is not None:
                remaining = max(0.0, deadline - monotonic())
            child.wait(timeout=remaining)
            for reader in readers:
                remaining = None
                if deadline is not None:
                    remaining = max(0.0, deadline - monotonic())
                reader.join(timeout=remaining)
            timed_out = any(reader.is_alive() for reader in readers)
        except TimeoutExpired:
            timed_out = True
    finally:
        try:
            if child.poll() is None:
                child.kill()
                child.wait(timeout=_CLEANUP_TIMEOUT)
        finally:
            stop_event.set()
            cleanup_deadline = monotonic() + _CLEANUP_TIMEOUT
            for reader in readers:
                reader.join(timeout=max(0.0, cleanup_deadline - monotonic()))
            child.stdout.close()
            child.stderr.close()
    stdout = _decode_output(b"".join(stdout_chunks))
    stderr = _decode_output(b"".join(stderr_chunks))
    if timed_out and live:
        assert timeout is not None
        raise TimeoutExpired(child.args, timeout, output=stdout, stderr=stderr)
    return stdout, stderr


def _decode_output(content: bytes) -> str:
    """Decode UTF-8 output, falling back to ISO-8859-1 for invalid UTF-8.

    Arguments:
        content: bytes to decode
    Returns:
        decoded text
    """
    try:
        return content.decode("utf-8")
    except UnicodeDecodeError:
        return content.decode("ISO-8859-1")


def _log_live_records(output: bytes) -> bytes:
    """Log complete live output records and return any incomplete remainder.

    Arguments:
        output: output bytes to log
    Returns:
        incomplete trailing output
    """
    record_start = 0
    for index, character in enumerate(output):
        if character not in {10, 13}:
            continue
        record = output[record_start:index]
        if record:
            logger.info(_decode_output(record))
        record_start = index + 1
    return output[record_start:]


def _read_stream(
    stream: IO[bytes], chunks: list[bytes], stop_event: Event, *, live: bool
):
    """Capture a nonblocking stream, optionally logging records, until EOF or cancel.

    Arguments:
        stream: subprocess output stream
        chunks: captured byte chunks
        stop_event: cancellation request that bounds draining pending bytes
        live: whether complete records are mirrored to logs
    """
    pending = b""
    drain_reads = 0
    try:
        while True:
            try:
                chunk = read(stream.fileno(), 4096)
            except BlockingIOError:
                if stop_event.is_set():
                    break
                stop_event.wait(0.05)
                continue
            if not chunk:
                break
            chunks.append(chunk)
            if live:
                pending = _log_live_records(pending + chunk)
            if stop_event.is_set():
                # Limit draining when an inherited pipe still has an active writer
                drain_reads += 1
                if drain_reads >= 16:
                    break
        if live and pending:
            logger.info(_decode_output(pending))
    finally:
        stream.close()
