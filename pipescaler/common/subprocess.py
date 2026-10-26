#  Copyright 2017-2026 Karl T Debiec. All rights reserved. This software may be modified
#  and distributed under the terms of the BSD license. See the LICENSE file for details.
"""Subprocess-related utility functions."""

from __future__ import annotations

import ctypes
import os
import signal
from collections.abc import Generator, Iterable, Mapping
from contextlib import contextmanager
from importlib import import_module
from logging import getLogger
from os import name as os_name
from os import read
from pathlib import Path
from subprocess import PIPE, Popen, TimeoutExpired
from threading import Event, Thread
from time import monotonic
from typing import IO, NoReturn

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

    If the timeout expires, kill the child and collect its remaining output.
    The resulting exit code is checked normally; TimeoutExpired is not propagated.
    Output is decoded as UTF-8, falling back to ISO-8859-1.

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
        ValueError: if the exit code is not accepted, including after a timeout
    """
    if acceptable_exitcodes is None:
        acceptable_exitcodes = [0]

    with _managed_process(command, cwd_path=cwd_path, env=env) as child:
        assert child.stdout is not None
        assert child.stderr is not None
        stdout_chunks: list[bytes] = []
        stderr_chunks: list[bytes] = []
        stdout_stop_event = Event()
        stderr_stop_event = Event()
        stdout_thread = Thread(
            target=_read_stream_chunks,
            args=(child.stdout, stdout_chunks, stdout_stop_event),
            daemon=True,
        )
        stderr_thread = Thread(
            target=_read_stream_chunks,
            args=(child.stderr, stderr_chunks, stderr_stop_event),
            daemon=True,
        )
        stdout_thread.name = f"pipescaler-reader-stdout-{child.pid}"
        stderr_thread.name = f"pipescaler-reader-stderr-{child.pid}"
        setattr(child, "_pipescaler_reader_threads", (stdout_thread, stderr_thread))
        setattr(
            child,
            "_pipescaler_reader_stop_events",
            (stdout_stop_event, stderr_stop_event),
        )
        stdout_thread.start()
        stderr_thread.start()

        deadline = monotonic() + timeout
        try:
            child.wait(timeout=max(0.0, deadline - monotonic()))
        except TimeoutExpired:
            timed_out = True
        else:
            timed_out = False

        if not timed_out:
            stdout_thread.join(timeout=max(0.0, deadline - monotonic()))
            stderr_thread.join(timeout=max(0.0, deadline - monotonic()))
            timed_out = stdout_thread.is_alive() or stderr_thread.is_alive()

        if timed_out:
            _kill_process_tree(child)
            try:
                child.wait(timeout=_CLEANUP_TIMEOUT)
            except TimeoutExpired:
                child.kill()
                child.wait(timeout=_CLEANUP_TIMEOUT)
            _stop_process_readers(child)

        stdout_str = _decode_output(b"".join(stdout_chunks))
        stderr_str = _decode_output(b"".join(stderr_chunks))
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
    On timeout, kill the child and raise TimeoutExpired with captured text in its
    output and stderr attributes.

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

    stdout_chunks = []
    stderr_chunks = []
    stdout_stop_event = Event()
    stderr_stop_event = Event()

    with _managed_process(command, cwd_path=cwd_path, env=env) as child:
        assert child.stdout is not None
        assert child.stderr is not None
        stdout_thread = Thread(
            target=_read_stream,
            args=(child.stdout, stdout_chunks, stdout_stop_event),
            daemon=True,
        )
        stderr_thread = Thread(
            target=_read_stream,
            args=(child.stderr, stderr_chunks, stderr_stop_event),
            daemon=True,
        )
        stdout_thread.name = f"pipescaler-reader-stdout-{child.pid}"
        stderr_thread.name = f"pipescaler-reader-stderr-{child.pid}"
        setattr(child, "_pipescaler_reader_threads", (stdout_thread, stderr_thread))
        setattr(
            child,
            "_pipescaler_reader_stop_events",
            (stdout_stop_event, stderr_stop_event),
        )
        stdout_thread.start()
        stderr_thread.start()

        exitcode = _wait_for_live_process(
            child,
            command,
            timeout,
            stdout_thread,
            stderr_thread,
            stdout_chunks,
            stderr_chunks,
        )

        stdout_str = _decode_output(b"".join(stdout_chunks))
        stderr_str = _decode_output(b"".join(stderr_chunks))

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


def _assign_process_job(child: Popen[bytes]):
    """Place a Windows child in a job so timeout cleanup owns its descendants.

    Arguments:
        child: child process to assign to a Windows job
    Raises:
        OSError: if the Windows job cannot be created or assigned
    """
    if os_name != "nt":
        return

    kernel32 = ctypes.WinDLL("kernel32", use_last_error=True)
    wintypes = import_module("ctypes.wintypes")
    kernel32.CreateJobObjectW.restype = wintypes.HANDLE
    kernel32.CreateJobObjectW.argtypes = (wintypes.LPVOID, wintypes.LPCWSTR)
    kernel32.OpenProcess.restype = wintypes.HANDLE
    kernel32.OpenProcess.argtypes = (wintypes.DWORD, wintypes.BOOL, wintypes.DWORD)
    kernel32.AssignProcessToJobObject.argtypes = (wintypes.HANDLE, wintypes.HANDLE)
    kernel32.AssignProcessToJobObject.restype = wintypes.BOOL
    kernel32.CloseHandle.argtypes = (wintypes.HANDLE,)
    kernel32.CloseHandle.restype = wintypes.BOOL
    job_handle = kernel32.CreateJobObjectW(None, None)
    process_handle = kernel32.OpenProcess(0x0101, False, child.pid)
    if not job_handle or not process_handle:
        if job_handle:
            kernel32.CloseHandle(job_handle)
        if process_handle:
            kernel32.CloseHandle(process_handle)
        if child.poll() is not None:
            return
        raise OSError("could not create Windows subprocess job")
    assigned = kernel32.AssignProcessToJobObject(job_handle, process_handle)
    kernel32.CloseHandle(process_handle)
    if not assigned:
        kernel32.CloseHandle(job_handle)
        if child.poll() is not None:
            return
        raise OSError("could not assign Windows subprocess job")
    setattr(child, "_pipescaler_job_handle", job_handle)


def _close_process_job(child: Popen[bytes]):
    """Release a Windows job handle after process cleanup is complete.

    Arguments:
        child: child process whose Windows job handle is released
    """
    if os_name == "nt":
        job_handle = getattr(child, "_pipescaler_job_handle", None)
        if job_handle is not None:
            kernel32 = ctypes.WinDLL("kernel32", use_last_error=True)
            wintypes = import_module("ctypes.wintypes")
            kernel32.CloseHandle.argtypes = (wintypes.HANDLE,)
            kernel32.CloseHandle.restype = wintypes.BOOL
            kernel32.CloseHandle(job_handle)
            setattr(child, "_pipescaler_job_handle", None)


def _close_process_streams(child: Popen[bytes]):
    """Stop stream readers within a bounded time and close their streams.

    Arguments:
        child: child process whose output streams are released
    """
    _stop_process_readers(child)
    if child.stdout is not None:
        child.stdout.close()
    if child.stderr is not None:
        child.stderr.close()


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


def _handle_live_timeout(  # noqa: PLR0913, PLR0917
    child: Popen[bytes],
    command: list[str],
    timeout: float,
    stdout_chunks: list[bytes],
    stderr_chunks: list[bytes],
) -> NoReturn:
    """Handle live subprocess timeout.

    Arguments:
        child: child process
        command: command run by the child process
        timeout: timeout that was exceeded
        stdout_chunks: standard output chunks read so far
        stderr_chunks: standard error chunks read so far
    Raises:
        TimeoutExpired: if the subprocess times out
    """
    _kill_process_tree(child)
    child.wait(timeout=_CLEANUP_TIMEOUT)
    _stop_process_readers(child)
    raise TimeoutExpired(
        command,
        timeout,
        output=_decode_output(b"".join(stdout_chunks)),
        stderr=_decode_output(b"".join(stderr_chunks)),
    )


def _kill_process_tree(child: Popen[bytes]):
    """Terminate a child and its descendants, ignoring an already-exited group.

    Arguments:
        child: child process whose process group or job is terminated
    """
    try:
        if os_name == "nt":
            kernel32 = ctypes.WinDLL("kernel32", use_last_error=True)
            wintypes = import_module("ctypes.wintypes")
            kernel32.TerminateJobObject.argtypes = (wintypes.HANDLE, wintypes.UINT)
            kernel32.TerminateJobObject.restype = wintypes.BOOL
            job_handle = getattr(child, "_pipescaler_job_handle", None)
            if job_handle is None or not kernel32.TerminateJobObject(job_handle, 1):
                child.kill()
        else:
            os.killpg(child.pid, signal.SIGKILL)
    except ProcessLookupError:
        pass
    except OSError:
        child.kill()


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


def _read_stream(stream: IO[bytes], chunks: list[bytes], stop_event: Event):
    """Read subprocess stream chunks and mirror records to logs.

    Arguments:
        stream: stream to read from
        chunks: list that collects the stream content
        stop_event: event that requests cancellation after pending output is drained
    """
    pending = b""
    stop_drain_reads = 0
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
            pending = _log_live_records(pending + chunk)
            if stop_event.is_set():
                stop_drain_reads += 1
                if stop_drain_reads >= 16:
                    break
        if pending:
            logger.info(_decode_output(pending))
    finally:
        stream.close()


def _read_stream_chunks(stream: IO[bytes], chunks: list[bytes], stop_event: Event):
    """Capture subprocess output chunks without emitting live log records.

    Arguments:
        stream: subprocess output stream
        chunks: list that collects the stream content
        stop_event: event that requests cancellation after pending output is drained
    """
    stop_drain_reads = 0
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
            if stop_event.is_set():
                stop_drain_reads += 1
                if stop_drain_reads >= 16:
                    break
    finally:
        stream.close()


def _stop_process_readers(child: Popen[bytes]):
    """Cancel owned pipe readers and wait for them within one cleanup window.

    Arguments:
        child: child process whose output readers are stopped
    """
    for stop_event in getattr(child, "_pipescaler_reader_stop_events", ()):
        stop_event.set()
    readers = getattr(child, "_pipescaler_reader_threads", ())
    deadline = monotonic() + _CLEANUP_TIMEOUT
    for reader in readers:
        reader.join(timeout=max(0.0, deadline - monotonic()))


def _wait_for_live_process(  # noqa: PLR0913, PLR0917
    child: Popen[bytes],
    command: list[str],
    timeout: float | None,
    stdout_thread: Thread,
    stderr_thread: Thread,
    stdout_chunks: list[bytes],
    stderr_chunks: list[bytes],
) -> int:
    """Wait for a live subprocess and its stream reader threads.

    Arguments:
        child: child process
        command: command run by the child process
        timeout: maximum time to await command's completion
        stdout_thread: thread reading standard output
        stderr_thread: thread reading standard error
        stdout_chunks: standard output chunks read so far
        stderr_chunks: standard error chunks read so far
    Returns:
        exitcode
    Raises:
        TimeoutExpired: if the subprocess times out
    """
    if timeout is None:
        exitcode = child.wait()
        stdout_thread.join()
        stderr_thread.join()
        return exitcode

    deadline = monotonic() + timeout
    try:
        exitcode = child.wait(timeout=max(0.0, deadline - monotonic()))
    except TimeoutExpired as exception:
        try:
            _handle_live_timeout(
                child,
                command,
                timeout,
                stdout_chunks,
                stderr_chunks,
            )
        except TimeoutExpired as timeout_exception:
            raise timeout_exception from exception

    stdout_thread.join(timeout=max(0.0, deadline - monotonic()))
    stderr_thread.join(timeout=max(0.0, deadline - monotonic()))
    if stdout_thread.is_alive() or stderr_thread.is_alive():
        _handle_live_timeout(
            child,
            command,
            timeout,
            stdout_chunks,
            stderr_chunks,
        )
    return exitcode


@contextmanager
def _managed_process(
    command: list[str],
    *,
    cwd_path: Path | None,
    env: Mapping[str, str] | None,
) -> Generator[Popen[bytes]]:
    """Own process-tree setup and bounded cleanup for one subprocess.

    Arguments:
        command: command to start
        cwd_path: working directory; None inherits the current directory
        env: complete child environment; None inherits the current environment
    Yields:
        started process while its process-tree resources remain owned
    """
    child = Popen(
        command,
        stdout=PIPE,
        stderr=PIPE,
        cwd=cwd_path,
        env=env,
        bufsize=0,
        start_new_session=os_name != "nt",
    )
    setattr(child, "_pipescaler_reader_threads", ())
    setattr(child, "_pipescaler_reader_stop_events", ())
    try:
        assert child.stdout is not None
        assert child.stderr is not None
        os.set_blocking(child.stdout.fileno(), False)
        os.set_blocking(child.stderr.fileno(), False)
        _assign_process_job(child)
        yield child
    finally:
        try:
            if child.poll() is None:
                try:
                    _kill_process_tree(child)
                except OSError:
                    child.kill()
                try:
                    child.wait(timeout=_CLEANUP_TIMEOUT)
                except TimeoutExpired:
                    child.kill()
                    child.wait(timeout=_CLEANUP_TIMEOUT)
        finally:
            try:
                _close_process_job(child)
            finally:
                _close_process_streams(child)


__all__ = ["run_command", "run_command_live"]
