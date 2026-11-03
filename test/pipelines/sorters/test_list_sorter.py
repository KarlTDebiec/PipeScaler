#  Copyright 2020-2026 Karl T Debiec. All rights reserved. This software may be modified
#  and distributed under the terms of the BSD license. See the LICENSE file for details.
"""Tests for ListSorter."""

from __future__ import annotations

from logging import WARNING
from pathlib import Path

import pytest

from pipescaler.common.file import get_temp_directory_path, get_temp_file_path
from pipescaler.image.core.pipelines import PipeImage
from pipescaler.pipelines.sorters import ListSorter
from pipescaler.testing.file import get_test_input_dir_path, get_test_input_path
from pipescaler.testing.fixture import parametrized_fixture


@parametrized_fixture(
    cls=ListSorter,
    params=[
        dict(
            basic=get_test_input_dir_path("basic"),
            extra=get_test_input_dir_path("extra"),
            novel=get_test_input_dir_path("novel"),
        ),
    ],
)
def sorter(request: pytest.FixtureRequest) -> ListSorter:
    """Pytest fixture that provides a ListSorter instance.

    Arguments:
        request: Pytest request fixture containing parameters
    Returns:
        Configured ListSorter instance
    """
    return ListSorter(**request.param)


@pytest.mark.parametrize(
    ("input_filename", "outlet"),
    [
        ("basic/L", "basic"),
        ("extra/1_L", "extra"),
        ("novel/L_solid", "novel"),
        ("split/LA_alpha_L", None),
    ],
)
def test(input_filename: str, outlet: str | None, sorter: ListSorter):
    """Test ListSorter routing based on predefined file lists.

    Arguments:
        input_filename: Input filename
        outlet: Expected outlet name or None
        sorter: ListSorter fixture instance
    """
    image = PipeImage(path=get_test_input_path(input_filename))
    assert sorter(image) == outlet

    # Test miscellaneous methods
    assert str(sorter)
    assert repr(sorter)
    assert sorter.outlets
    assert sorter.help_markdown()


@pytest.mark.parametrize(
    ("input_filename", "outlet"),
    [
        ("basic/L", "basic"),
        ("extra/1_L", "extra"),
        ("novel/L_solid", "novel"),
        ("split/LA_alpha_L", None),
    ],
)
def test_text_file(input_filename: str, outlet: str | None):
    """Test ListSorter loading lists from text files.

    Arguments:
        input_filename: Input filename
        outlet: Expected outlet name or None
    """
    with get_temp_file_path() as basic_file_path:
        with open(basic_file_path, "w") as basic_file:
            basic_file.write("L\n")
        with get_temp_file_path() as extra_file_path:
            with open(extra_file_path, "w") as extra_file:
                extra_file.write("1_L\n")
            with get_temp_file_path() as novel_file_path:
                with open(novel_file_path, "w") as novel_file:
                    novel_file.write("L_solid\n")
                sorter = ListSorter(
                    basic=str(basic_file_path),
                    extra=str(extra_file_path),
                    novel=str(novel_file_path),
                )

    image = PipeImage(path=get_test_input_path(input_filename))
    assert sorter(image) == outlet


def test_exclusions():
    """Test ListSorter excluding system files like .DS_Store and Thumbs.db."""
    with get_temp_directory_path() as basic_dir_path:
        (basic_dir_path / ".DS_Store").touch()
        (basic_dir_path / "Thumbs.db").touch()
        (basic_dir_path / "desktop.ini").touch()
        sorter = ListSorter(basic=basic_dir_path)
        assert sorter.outlets_by_filename == {}


@pytest.mark.parametrize("allow_duplicates", [False, True])
def test_repr_round_trip(allow_duplicates: bool):
    """Test ListSorter repr round-trip recreation with both duplicate policies.

    Arguments:
        allow_duplicates: whether to permit names assigned to multiple outlets
    """
    sorter = ListSorter(
        allow_duplicates=allow_duplicates,
        basic=get_test_input_dir_path("basic"),
        extra=get_test_input_dir_path("extra"),
        novel=get_test_input_dir_path("novel"),
    )
    recreated = eval(repr(sorter))
    assert recreated.outlets == sorter.outlets
    assert recreated.outlets_by_filename == sorter.outlets_by_filename
    assert repr(recreated) == repr(sorter)


@pytest.mark.parametrize("allow_duplicates", [False, True])
@pytest.mark.parametrize("reverse_outlets", [False, True])
@pytest.mark.parametrize(
    "source_is_directory",
    [(False, False), (False, True), (True, False), (True, True)],
)
def test_conflicting_outlets(
    tmp_path: Path,
    caplog: pytest.LogCaptureFixture,
    allow_duplicates: bool,
    reverse_outlets: bool,
    source_is_directory: tuple[bool, bool],
):
    """Reject overlapping outlets unless explicitly allowed, preserving precedence.

    Arguments:
        tmp_path: temporary directory for outlet sources
        caplog: captured log messages
        allow_duplicates: whether to permit conflicting assignments
        reverse_outlets: whether to reverse the configured outlet order
        source_is_directory: whether each outlet source is a directory
    """
    outlet_paths: dict[str, Path] = {}
    for outlet, is_directory in zip(
        ("first", "second"), source_is_directory, strict=True
    ):
        source_path = tmp_path / outlet
        if is_directory:
            source_path.mkdir()
            (source_path / "L.png").touch()
        else:
            source_path.write_text("L\n", encoding="utf-8")
        outlet_paths[outlet] = source_path
    if reverse_outlets:
        outlet_paths = dict(reversed(outlet_paths.items()))

    message = "<ListSorter>: names assigned to multiple outlets: 'L': 'first', 'second'"
    if not allow_duplicates:
        with pytest.raises(ValueError) as error:
            ListSorter(allow_duplicates=False, **outlet_paths)
        assert str(error.value) == message
        assert not caplog.records
    else:
        sorter = ListSorter(allow_duplicates=True, **outlet_paths)
        image = PipeImage(path=get_test_input_path("basic/L"))
        if reverse_outlets:
            expected_outlet = "first"
        else:
            expected_outlet = "second"
        assert sorter(image) == expected_outlet
        assert caplog.record_tuples == [
            (
                "root",
                WARNING,
                f"{message}; last configured outlet wins",
            )
        ]

        recreated = eval(repr(sorter))
        assert recreated(image) == expected_outlet
        assert repr(recreated) == repr(sorter)


def test_conflicting_outlets_report_all_names(tmp_path: Path):
    """Report all conflicting names and outlets together in a stable order.

    Arguments:
        tmp_path: temporary directory for outlet lists
    """
    outlet_paths: dict[str, Path] = {}
    for outlet in ("third", "second", "first"):
        list_path = tmp_path / f"{outlet}.txt"
        list_path.write_text("RGB\nL\nRGB\n", encoding="utf-8")
        outlet_paths[outlet] = list_path

    with pytest.raises(ValueError) as error:
        ListSorter(
            third=outlet_paths["third"],
            second=outlet_paths["second"],
            first=outlet_paths["first"],
        )

    assert str(error.value) == (
        "<ListSorter>: names assigned to multiple outlets: "
        "'L': 'first', 'second', 'third'; 'RGB': 'first', 'second', 'third'"
    )


@pytest.mark.parametrize("allow_duplicates", [False, True])
def test_repeated_names_within_outlet(
    tmp_path: Path, caplog: pytest.LogCaptureFixture, allow_duplicates: bool
):
    """Allow repeated names within a file, directory, and list of sources.

    Arguments:
        tmp_path: temporary directory for outlet sources
        caplog: captured log messages
        allow_duplicates: whether to permit names assigned to multiple outlets
    """
    list_path = tmp_path / "names.txt"
    list_path.write_text("L\nL\n", encoding="utf-8")
    dir_path = tmp_path / "images"
    dir_path.mkdir()
    (dir_path / "L.png").touch()
    (dir_path / "L.jpg").touch()

    sorter = ListSorter(
        allow_duplicates=allow_duplicates, only=[list_path, dir_path, list_path]
    )

    assert sorter.outlets_by_filename == {"L": "only"}
    assert sorter(PipeImage(path=get_test_input_path("basic/L"))) == "only"
    assert not caplog.records


def test_ignored_names_do_not_conflict(
    tmp_path: Path, caplog: pytest.LogCaptureFixture
):
    """Ignore blank lines, comments, and excluded stems in overlapping sources.

    Arguments:
        tmp_path: temporary directory for outlet sources
        caplog: captured log messages
    """
    first_path = tmp_path / "first.txt"
    second_path = tmp_path / "second.txt"
    for list_path in (first_path, second_path):
        list_path.write_text(
            "\n   \n# comment\n.DS_Store\nThumbs\ndesktop\n", encoding="utf-8"
        )
    dir_path = tmp_path / "images"
    dir_path.mkdir()
    (dir_path / ".DS_Store").touch()
    (dir_path / "Thumbs.db").touch()
    (dir_path / "desktop.ini").touch()

    sorter = ListSorter(first=first_path, second=second_path, third=dir_path)

    assert sorter.outlets_by_filename == {}
    assert not caplog.records
