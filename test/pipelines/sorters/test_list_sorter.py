#  Copyright 2020-2025 Karl T Debiec. All rights reserved. This software may be modified
#  and distributed under the terms of the BSD license. See the LICENSE file for details.
"""Tests for ListSorter."""

from __future__ import annotations

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
def sorter(request) -> ListSorter:
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
def test(input_filename: str, outlet: str | None, sorter: ListSorter) -> None:
    image = PipeImage(path=get_test_input_path(input_filename))
    assert sorter(image) == outlet

    # Test miscellaneous methods
    print(sorter)
    print(repr(sorter))
    print(sorter.outlets)
    print(sorter.help_markdown())


@pytest.mark.parametrize(
    ("input_filename", "outlet"),
    [
        ("basic/L", "basic"),
        ("extra/1_L", "extra"),
        ("novel/L_solid", "novel"),
        ("split/LA_alpha_L", None),
    ],
)
def test_text_file(input_filename: str, outlet: str | None) -> None:
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


def test_exclusions() -> None:
    with get_temp_directory_path() as basic_directory_path:
        (basic_directory_path / ".DS_Store").touch()
        (basic_directory_path / "Thumbs.db").touch()
        (basic_directory_path / "desktop.ini").touch()
        sorter = ListSorter(basic=basic_directory_path)
        assert sorter.outlets_by_filename == {}
