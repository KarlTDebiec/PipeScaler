#  Copyright 2017-2026 Karl T Debiec. All rights reserved. This software may be modified
#  and distributed under the terms of the BSD license. See the LICENSE file for details.
"""ABC for command-line interfaces."""

from __future__ import annotations

import re
from abc import ABC, abstractmethod
from argparse import (
    SUPPRESS,
    Action,
    ArgumentParser,
    Namespace,
    RawDescriptionHelpFormatter,
    _SubParsersAction,  # noqa pylint
)
from collections.abc import Iterable, Sequence
from datetime import datetime
from inspect import cleandoc
from logging import FileHandler, Formatter, getLogger
from pathlib import Path
from sys import argv
from typing import Any, cast

from .logs import DEFAULT_LOG_FORMAT, configure_logging

__all__ = ["CommandLineInterface"]

logger = getLogger(__name__)


class CommandLineInterface(ABC):
    """ABC for command-line interfaces."""

    @classmethod
    def add_arguments_to_argparser(cls, parser: ArgumentParser):
        """Add arguments to a nascent argument parser.

        Arguments:
            parser: Nascent argument parser
        """
        verbosity = parser.add_mutually_exclusive_group()
        parser_id = id(parser)
        aggregated = isinstance(parser, _CliArgumentParser)
        if aggregated:
            verbosity_dest = f"_cli_verbosity_{parser_id}"
            quiet_dest = f"_cli_quiet_{parser_id}"
            log_file_dest = f"_cli_log_file_{parser_id}"
            verbosity_default = SUPPRESS
            quiet_default = SUPPRESS
            log_file_default = SUPPRESS
        else:
            verbosity_dest = "verbosity"
            quiet_dest = "verbosity"
            log_file_dest = "log_file"
            verbosity_default = 1
            quiet_default = None
            log_file_default = None
        verbosity.add_argument(
            "-v",
            "--verbose",
            action=_VerbosityAction,
            nargs=0,
            default=verbosity_default,
            dest=verbosity_dest,
            help=(
                "increase console verbosity; use -v for info and -vv for debug "
                "(default: warnings and errors)"
            ),
        )
        verbosity.add_argument(
            "-q",
            "--quiet",
            action="store_const",
            const=0,
            dest=quiet_dest,
            default=quiet_default,
            help="show only errors",
        )

        timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
        parser.add_argument(
            "-l",
            "--log-file",
            nargs="?",
            const=f"{cls.name()}.{timestamp}.log",
            required=False,
            default=log_file_default,
            dest=log_file_dest,
            type=str,
            help=(
                "write logs to an optional path; without a value, use "
                "<command>.YYYY-MM-DD_hh-mm-ss.log in the current directory"
            ),
        )
        for action_group in parser._action_groups:  # noqa: SLF001
            if action_group.title in {"optional arguments", "options"}:
                action_group.title = "additional arguments"

    @classmethod
    def argparser(
        cls, *, subparsers: _SubParsersAction | None = None
    ) -> ArgumentParser:
        """Construct argument parser.

        Arguments:
            subparsers: Subparsers group to which a new subparser will be added; if
              None, a new ArgumentParser will be created
        Returns:
            Argument parser
        """
        if not subparsers:
            parser = _CliArgumentParser(
                description=str(cls.description()),
                formatter_class=RawDescriptionHelpFormatter,
            )
        else:
            parser = subparsers.add_parser(
                name=cls.name(),
                description=cls.description(),
                help=cls.help(),
                formatter_class=RawDescriptionHelpFormatter,
            )

        cls.add_arguments_to_argparser(parser)

        return parser

    @classmethod
    def description(cls) -> str:
        """Get the long description displayed below usage.

        Returns:
            long tool description
        """
        return cleandoc(cls.__doc__) if cls.__doc__ else ""

    @classmethod
    def help(cls) -> str:
        """Get the short description used when this tool is a subparser.

        Returns:
            short tool description
        """
        text = re.split(r"\.\s+", str(cls.description()))[0].rstrip(".")
        return text[0].lower() + text[1:]

    @classmethod
    def main(cls, arguments: Sequence[str] | None = None):
        """Execute from command line.

        Arguments:
            arguments: explicit tokens, or process arguments when omitted
        """
        parser = cls.argparser()
        kwargs = vars(parser.parse_args(arguments))

        # Configure logging
        verbosity = kwargs.pop("verbosity", 1)
        configure_logging(verbosity)

        # File logging
        log_file = kwargs.pop("log_file")
        if log_file:
            log_file_path = Path(log_file).resolve()
            file_handler = FileHandler(log_file_path, encoding="utf-8")
            file_handler.setLevel(getLogger().level)
            formatter = Formatter(DEFAULT_LOG_FORMAT)
            file_handler.setFormatter(formatter)
            getLogger().addHandler(file_handler)
            logger.info(f"Logging to {log_file_path} at level {getLogger().level}")

        cls._main(**kwargs)

    @classmethod
    def name(cls) -> str:
        """Get the name used to define this tool as a subparser.

        Returns:
            subparser name
        """
        name = cls.__name__
        if name.endswith("Cli"):
            name = name[:-3]
        return name.lower()

    @staticmethod
    def log_command_line():
        """Log the command line with which the script was run."""
        args = argv[:]
        command_line = " ".join(args)
        logger.info(f"Run with command line: {command_line}")

    @classmethod
    @abstractmethod
    def _main(cls, *args: Any, **kwargs: Any):
        """Execute with provided command-line arguments.

        Arguments:
            *args: positional command-line arguments
            **kwargs: parsed command-line arguments
        """
        raise NotImplementedError()


class _VerbosityAction(Action):
    """Increment verbosity for one occurrence of the option."""

    def __call__(
        self,
        parser: ArgumentParser,
        namespace: Namespace,
        values: object,
        option_string: str | None = None,
    ):
        """Increase verbosity for one occurrence of the option.

        Arguments:
            parser: active parser
            namespace: parsed arguments
            values: unused value for this zero-argument option
            option_string: option used to invoke the action
        """
        initial = 0
        if not self.dest.startswith("_cli_verbosity_"):
            initial = 1
        setattr(namespace, self.dest, getattr(namespace, self.dest, initial) + 1)


class _CliArgumentParser(ArgumentParser):
    """Combine common options parsed at different command levels."""

    def parse_args(
        self, args: Iterable[str] | None = None, namespace: Namespace | None = None
    ) -> Namespace:
        """Parse arguments and combine common options from each command level.

        Arguments:
            args: argument tokens
            namespace: initial namespace
        Returns:
            parsed arguments with normalized common options
        """
        parsed = cast(Namespace, super().parse_args(args, namespace))
        values = vars(parsed)
        verbosity = 1 + sum(
            value for key, value in values.items() if key.startswith("_cli_verbosity_")
        )
        if any(key.startswith("_cli_quiet_") for key in values):
            verbosity = 0
        log_files = [
            value for key, value in values.items() if key.startswith("_cli_log_file_")
        ]
        for key in tuple(values):
            if key.startswith(("_cli_verbosity_", "_cli_quiet_", "_cli_log_file_")):
                del values[key]
        values["verbosity"] = verbosity
        if log_files:
            values["log_file"] = log_files[-1]
        else:
            values["log_file"] = None
        return parsed
