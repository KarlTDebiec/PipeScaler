#  Copyright 2026 Karl T Debiec. All rights reserved. This software may be modified
#  and distributed under the terms of the BSD license. See the LICENSE file for details.
"""Tests for CLI discovery through installed package entry points."""

from __future__ import annotations

from collections.abc import Iterator
from importlib.metadata import EntryPoint
from typing import Any
from unittest.mock import patch

import pytest

import pipescaler.common.cli.entry_points as command_entries
from pipescaler.common.command_line_interface import CommandLineInterface


class ExtraCli(CommandLineInterface):
    """Concrete extension command for registration tests."""

    @classmethod
    def _main(cls, **kwargs: Any):
        """Accept parsed options without executing an operation.

        Arguments:
            **kwargs: ignored command options
        """


def test_cache_loads_once_and_returns_independent_registries():
    """Reuse extension classes without exposing the cached registration collection."""
    entry = EntryPoint(name="extra", value="extension:ExtraCli", group="test.commands")
    with (
        patch.object(command_entries, "entry_points", return_value=[entry]),
        patch.object(EntryPoint, "load", return_value=ExtraCli) as load,
    ):
        first = command_entries.get_cli_commands(
            {}, group=entry.group, base_class=CommandLineInterface
        )
        first.clear()
        second = command_entries.get_cli_commands(
            {}, group=entry.group, base_class=CommandLineInterface
        )

    assert second == {"extra": ExtraCli}
    load.assert_called_once_with()


def test_entry_point_name_must_match_command_name():
    """Prevent parser registration and execution lookup from using different names."""
    entry = EntryPoint(
        name="different", value="extension:ExtraCli", group="test.commands"
    )
    with (
        patch.object(command_entries, "entry_points", return_value=[entry]),
        patch.object(EntryPoint, "load", return_value=ExtraCli),
        pytest.raises(ValueError, match="name must match"),
    ):
        command_entries.get_cli_commands(
            {}, group=entry.group, base_class=CommandLineInterface
        )


def test_load_failure_retains_context():
    """Identify a broken registration and preserve the original import failure."""
    entry = EntryPoint(name="extra", value="missing:ExtraCli", group="test.commands")
    failure = ModuleNotFoundError("missing extension dependency")
    with (
        patch.object(command_entries, "entry_points", return_value=[entry]),
        patch.object(EntryPoint, "load", side_effect=failure),
        pytest.raises(ValueError) as raised,
    ):
        command_entries.get_cli_commands(
            {}, group=entry.group, base_class=CommandLineInterface
        )

    assert raised.value.__cause__ is failure
    assert "extra" in str(raised.value)
    assert entry.group in str(raised.value)
    assert "missing extension dependency" in str(raised.value)


def test_no_extensions_preserves_builtins():
    """Keep existing commands available without installed extensions."""
    builtins = {"extra": ExtraCli}

    commands = command_entries.get_cli_commands(
        builtins, group="test.commands", base_class=CommandLineInterface
    )

    assert commands == builtins
    assert commands is not builtins


def test_required_base_is_checked_even_after_another_group_load():
    """Keep base-class validation specific to each registry's required contract."""

    class RequiredCli(ExtraCli):
        """More specific CLI contract required by this registry."""

    entry = EntryPoint(name="extra", value="extension:ExtraCli", group="test.commands")
    with (
        patch.object(command_entries, "entry_points", return_value=[entry]),
        patch.object(EntryPoint, "load", return_value=ExtraCli),
    ):
        command_entries.get_cli_commands(
            {}, group=entry.group, base_class=CommandLineInterface
        )
        with pytest.raises(ValueError, match="concrete RequiredCli subclass"):
            command_entries.get_cli_commands(
                {}, group=entry.group, base_class=RequiredCli
            )


@pytest.fixture(autouse=True)
def isolated_discovery() -> Iterator[None]:
    """Keep cached registrations and installed extensions isolated between tests.

    Yields:
        control while entry-point discovery is isolated
    """
    command_entries._load_cli_commands.cache_clear()
    with patch.object(command_entries, "entry_points", return_value=[]):
        yield
    command_entries._load_cli_commands.cache_clear()


@pytest.mark.parametrize("duplicate_builtin", [False, True])
def test_duplicate_names_are_rejected(duplicate_builtin: bool):
    """Reject extension collisions with both built-ins and other extensions.

    Arguments:
        duplicate_builtin: whether the conflicting name belongs to a built-in
    """
    entry = EntryPoint(name="extra", value="extension:ExtraCli", group="test.commands")
    entries = [entry] if duplicate_builtin else [entry, entry]
    builtins = {"extra": ExtraCli} if duplicate_builtin else {}
    with (
        patch.object(command_entries, "entry_points", return_value=entries),
        patch.object(EntryPoint, "load", return_value=ExtraCli),
        pytest.raises(ValueError, match="duplicates command 'extra'"),
    ):
        command_entries.get_cli_commands(
            builtins, group=entry.group, base_class=CommandLineInterface
        )


@pytest.mark.parametrize("loaded", [None, object, ExtraCli(), CommandLineInterface])
def test_wrong_or_abstract_types_are_rejected(loaded: object):
    """Require a concrete CLI class instead of instances, functions, or abstractions.

    Arguments:
        loaded: invalid object returned by an entry point
    """
    entry = EntryPoint(name="extra", value="extension:command", group="test.commands")
    with (
        patch.object(command_entries, "entry_points", return_value=[entry]),
        patch.object(EntryPoint, "load", return_value=loaded),
        pytest.raises(ValueError, match="concrete CommandLineInterface subclass"),
    ):
        command_entries.get_cli_commands(
            {}, group=entry.group, base_class=CommandLineInterface
        )
