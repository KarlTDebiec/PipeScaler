#  Copyright 2017-2026 Karl T Debiec. All rights reserved. This software may be modified
#  and distributed under the terms of the BSD license. See the LICENSE file for details.
"""Portable helpers shared by common-module tests."""

from __future__ import annotations

from contextlib import redirect_stderr, redirect_stdout
from inspect import getfile
from io import StringIO
from pathlib import Path

from pytest import mark, raises, skip

from pipescaler.common import CommandLineInterface
from pipescaler.common.testing import run_cli_with_args

parametrize = mark.parametrize


def assert_cli_help(cli: tuple[type[CommandLineInterface], ...]):
    """Assert that a CLI tuple shows help text.

    Arguments:
        cli: CLI class tuple with optional subcommands
    """
    subcommands = build_subcommands(cli)
    stdout = StringIO()
    stderr = StringIO()
    with raises(SystemExit) as excinfo:
        with redirect_stdout(stdout):
            with redirect_stderr(stderr):
                run_cli_with_args(cli[0], f"{subcommands} -h".strip())
    assert excinfo.value.code == 0
    assert stdout.getvalue().startswith(get_usage_prefix(cli))
    assert stderr.getvalue() == ""


def assert_cli_usage(cli: tuple[type[CommandLineInterface], ...]):
    """Assert that a CLI tuple shows usage on missing args.

    Arguments:
        cli: CLI class tuple with optional subcommands
    """
    subcommands = build_subcommands(cli)
    stdout = StringIO()
    stderr = StringIO()
    with raises(SystemExit) as excinfo:
        with redirect_stdout(stdout):
            with redirect_stderr(stderr):
                run_cli_with_args(cli[0], subcommands)
    assert excinfo.value.code == 2
    assert stdout.getvalue() == ""
    expected_usage_prefix = get_usage_prefix(cli)
    actual_stdout = stdout.getvalue()
    actual_stderr = stderr.getvalue()
    assert actual_stderr.startswith(expected_usage_prefix), (
        "Expected stderr to start with:\n"
        f"{expected_usage_prefix!r}\n"
        "Actual stderr:\n"
        f"{actual_stderr!r}\n"
        "Actual stdout:\n"
        f"{actual_stdout!r}"
    )


def build_subcommands(cli: tuple[type[CommandLineInterface], ...]) -> str:
    """Build subcommand string for a CLI tuple.

    Arguments:
        cli: CLI class tuple with optional subcommands
    Returns:
        subcommand string to append to the base CLI
    """
    return " ".join(f"{command.name()}" for command in cli[1:])


def create_symlink_or_skip(
    symlink_path: Path, target_path: Path, *, target_is_directory: bool = False
):
    """Create a symlink, skipping when Windows privileges do not allow it.

    Arguments:
        symlink_path: path at which to create the symlink
        target_path: symlink target path
        target_is_directory: whether the target is a directory
    Raises:
        OSError: if a filesystem operation fails
    """
    try:
        symlink_path.symlink_to(target_path, target_is_directory=target_is_directory)
    except OSError as exc:
        if getattr(exc, "winerror", None) == 1314:
            skip("Windows symlink privilege is not available")
        raise


def get_usage_prefix(cli: tuple[type[CommandLineInterface], ...]) -> str:
    """Get expected usage prefix for a CLI tuple.

    Arguments:
        cli: CLI class tuple with optional subcommands
    Returns:
        expected usage prefix
    """
    subcommands = build_subcommands(cli)
    prefix = f"usage: {Path(getfile(cli[0])).name}"
    if subcommands:
        return f"{prefix} {subcommands}"
    return prefix
