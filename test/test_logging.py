#  Copyright 2026 Karl T Debiec. All rights reserved. This software may be modified
#  and distributed under the terms of the BSD license. See the LICENSE file for details.
"""Regression coverage for library logging and CLI logging configuration."""

from __future__ import annotations

from contextlib import redirect_stderr, suppress
from inspect import cleandoc
from io import StringIO
from logging import DEBUG, INFO, NOTSET, WARNING, getLogger
from pathlib import Path
from subprocess import run
from sys import executable

import pytest
from PIL import Image

from pipescaler.cli.pipescaler_cli import PipeScalerCli
from pipescaler.common import package_root
from pipescaler.common.testing import run_cli_with_args
from pipescaler.image.cli.processors.mode_cli import ModeCli
from pipescaler.image.core.pipelines.pipe_image import PipeImage
from pipescaler.image.core.sorting import citra_sort
from pipescaler.pipelines.sorters.list_sorter import ListSorter
from pipescaler.pipelines.sorters.regex_sorter import RegexSorter


@pytest.mark.parametrize(
    ("options", "verbosity"),
    [(["-q"], 0), ([], 1), (["-v"], 2), (["-vv"], 3)],
)
def test_cli_console_and_file_logging(
    tmp_path: Path, options: list[str], verbosity: int
):
    """Keep verbosity and single console/file delivery across repeated CLI calls.

    Arguments:
        tmp_path: temporary image and log directory
        options: verbosity options passed through root CLI dispatch
        verbosity: expected verbosity level
    """
    input_path = tmp_path / "sample.png"
    output_path = tmp_path / "output.png"
    log_file_path = tmp_path / "output.log"
    list_path = tmp_path / "names.txt"
    Image.new("RGB", (1, 1)).save(input_path)
    list_path.write_text("sample\n", encoding="utf-8")
    stderr = StringIO()
    root_logger = getLogger()
    handlers, level = root_logger.handlers[:], root_logger.level
    with redirect_stderr(stderr):
        try:
            for _ in range(2):
                run_cli_with_args(
                    PipeScalerCli,
                    f'{" ".join(options)} -l "{log_file_path}" '
                    f'image process resize "{input_path}" "{output_path}" '
                    "--scale 1 --resample nearest",
                )
                output_path.unlink()
                image = PipeImage(path=input_path, detach_file=True)
                assert image.image.size == (1, 1)
                ListSorter(allow_duplicates=True, first=list_path, second=list_path)
                with suppress(ValueError):
                    citra_sort("invalid.png")
        finally:
            for handler in root_logger.handlers:
                if handler not in handlers:
                    handler.close()
            root_logger.handlers[:] = handlers
            root_logger.setLevel(level)

    assert stderr.getvalue() == log_file_path.read_text(encoding="utf-8")
    for level, module_name, minimum_verbosity in [
        ("ERROR", "pipescaler.image.core.sorting", 0),
        ("WARNING", "pipescaler.pipelines.sorters.list_sorter", 1),
        ("INFO", "pipescaler.image.core.cli.image_processor_cli", 2),
        ("DEBUG", "pipescaler.image.core.pipelines.pipe_image", 3),
    ]:
        expected_count = 2 if verbosity >= minimum_verbosity else 0
        assert stderr.getvalue().count(f"{level}: {module_name}:") == expected_count


@pytest.mark.parametrize(
    ("root_options", "image_options", "leaf_options", "expected"),
    [
        (["-v"], ["-vv"], ["-v"], (2, None)),
        (["-vv"], [], [], (3, None)),
        (["-q"], [], [], (0, None)),
        (["-vv"], ["-v"], [], (2, None)),
        (["-v"], [], ["-q"], (0, None)),
        (["-l", "root.log"], [], [], (1, "root.log")),
        (["-l", "root.log"], ["-l", "image.log"], [], (1, "image.log")),
        (["-l", "root.log"], ["-l", "image.log"], ["-l", "leaf.log"], (1, "leaf.log")),
        (["-q"], ["-v"], ["-v"], (2, None)),
    ],
)
def test_cli_nested_logging_options(
    tmp_path: Path,
    root_options: list[str],
    image_options: list[str],
    leaf_options: list[str],
    expected: tuple[int, str | None],
):
    """Preserve inherited logging options and honor explicit child overrides.

    Arguments:
        tmp_path: directory for a placeholder input image
        root_options: logging arguments at the root
        image_options: logging arguments on the image command
        leaf_options: logging arguments on the image processor
        expected: selected verbosity and log file
    """
    input_path = tmp_path / "input.png"
    input_path.touch()
    output_path = tmp_path / "output.png"
    arguments = [str(input_path), str(output_path), "--mode", "RGB"]
    parser = PipeScalerCli.argparser()
    parsed = parser.parse_args(
        [
            *root_options,
            "image",
            *image_options,
            "process",
            "mode",
            *leaf_options,
            *arguments,
        ]
    )
    defaults = parser.parse_args(["image", "process", "mode", *arguments])

    assert (parsed.verbosity, parsed.log_file) == expected
    assert (defaults.verbosity, defaults.log_file) == (1, None)


def test_cli_standalone_logging_options(tmp_path: Path):
    """Count standalone verbosity flags and keep options local to each parse.

    Arguments:
        tmp_path: directory for a placeholder input image
    """
    input_path = tmp_path / "input.png"
    input_path.touch()
    output_path = tmp_path / "output.png"
    arguments = [str(input_path), str(output_path), "--mode", "RGB"]
    parser = ModeCli.argparser()
    configured = parser.parse_args(["-v", "-v", "-l", "leaf.log", *arguments])
    defaults = parser.parse_args(arguments)

    assert (configured.verbosity, configured.log_file) == (3, "leaf.log")
    assert (defaults.verbosity, defaults.log_file) == (1, None)


@pytest.mark.parametrize("configured", [False, True])
def test_library_preserves_application_logging(configured: bool):
    """Leave root handlers and levels intact, including an unconfigured application.

    A fresh process detects implicit basicConfig calls without pytest handlers.

    Arguments:
        configured: whether the application installs its own handler before import
    """
    result = run(
        [
            executable,
            "-c",
            cleandoc(
                """
                import logging
                import sys
                from contextlib import suppress
                from io import StringIO

                root = logging.getLogger()
                root.setLevel(logging.ERROR)
                handler = logging.StreamHandler(StringIO())
                handler.setLevel(logging.ERROR)
                formatter = logging.Formatter("application: %(message)s")
                handler.setFormatter(formatter)
                app_filter = logging.Filter()
                root.addFilter(app_filter)
                if sys.argv[1] == "True":
                    root.addHandler(handler)
                handlers = root.handlers[:]
                filters = root.filters[:]

                from pipescaler.image.core.sorting import citra_sort

                with suppress(ValueError):
                    citra_sort("invalid.png")

                assert root.level == logging.ERROR
                assert root.handlers == handlers
                assert root.filters == filters
                assert handler.level == logging.ERROR
                assert handler.formatter is formatter
                logger = logging.getLogger("pipescaler.image.core.sorting")
                assert logger.level == logging.NOTSET
                assert logger.handlers == []
                assert logger.propagate
                """
            ),
            str(configured),
        ],
        check=False,
        cwd=package_root.parent,
        capture_output=True,
        text=True,
        encoding="utf-8",
        timeout=60,
    )
    assert result.returncode == 0, result.stderr


@pytest.mark.parametrize(
    ("levels", "disabled", "expected"),
    [
        ((INFO, NOTSET), False, True),
        ((WARNING, NOTSET), False, False),
        ((WARNING, INFO), False, True),
        ((INFO, WARNING), False, False),
        ((INFO, INFO), True, False),
    ],
)
def test_package_and_module_logging_controls(
    caplog: pytest.LogCaptureFixture,
    monkeypatch: pytest.MonkeyPatch,
    levels: tuple[int, int],
    disabled: bool,
    expected: bool,
):
    """Honor package thresholds, module overrides, and module disabling.

    Arguments:
        caplog: captured log records
        monkeypatch: fixture restoring logger state
        levels: package threshold and explicit module threshold or NOTSET to inherit
        disabled: whether to disable the emitting module
        expected: whether the sorter diagnostic should be emitted
    """
    package_level, module_level = levels
    module_name = "pipescaler.pipelines.sorters.regex_sorter"
    monkeypatch.setattr(getLogger(module_name), "disabled", disabled)
    image = PipeImage(image=Image.new("RGB", (1, 1)), name="sample")
    with (
        caplog.at_level(DEBUG),
        caplog.at_level(package_level, logger="pipescaler"),
        caplog.at_level(module_level, logger=module_name),
    ):
        RegexSorter("sample")(image)

    if expected:
        assert caplog.record_tuples == [
            (module_name, INFO, "<RegexSorter>: 'sample' matches 'matched'")
        ]
    else:
        assert not caplog.records


@pytest.mark.parametrize("root_level", [WARNING, DEBUG])
def test_records_identify_emitting_modules(
    tmp_path: Path, caplog: pytest.LogCaptureFixture, root_level: int
):
    """Capture PipeScaler diagnostics independently of dependency logging.

    Arguments:
        tmp_path: temporary image directory
        caplog: captured log records
        root_level: application logging threshold, including dependency debug output
    """
    input_path = tmp_path / "sample.png"
    Image.new("RGB", (1, 1)).save(input_path)
    image = PipeImage(path=input_path, detach_file=True)
    with (
        caplog.at_level(root_level),
        caplog.at_level(DEBUG, logger="pipescaler"),
    ):
        assert image.image.size == (1, 1)
        assert RegexSorter("sample")(image) == "matched"

    assert [
        record for record in caplog.record_tuples if record[0].startswith("pipescaler.")
    ] == [
        (
            "pipescaler.image.core.pipelines.pipe_image",
            DEBUG,
            f"<PipeImage 'sample'>: Opening image 'sample' from '{input_path}'",
        ),
        (
            "pipescaler.pipelines.sorters.regex_sorter",
            INFO,
            "<RegexSorter>: 'sample' matches 'matched'",
        ),
    ]
