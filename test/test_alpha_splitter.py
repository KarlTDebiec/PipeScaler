#!/usr/bin/env python
#   test_alpha_splitter.py
#
#   Copyright (C) 2020-2022 Karl T Debiec
#   All rights reserved.
#
#   This software may be modified and distributed under the terms of the
#   BSD license. See the LICENSE file for details.
import pytest
from PIL import Image
from shared import get_infile, xfail_unsupported_mode

from pipescaler.common import temporary_filename
from pipescaler.core import remove_palette_from_image
from pipescaler.splitters import AlphaSplitter


@pytest.fixture()
def alpha_splitter(request) -> AlphaSplitter:
    return AlphaSplitter(**request.param)


@pytest.mark.parametrize(
    ("infile", "expected_alpha_mode", "alpha_splitter"),
    [
        xfail_unsupported_mode()("1", "L", {}),
        xfail_unsupported_mode()("L", "L", {}),
        ("LA", "L", {"alpha_mode": "L"}),
        ("LA", "L", {"alpha_mode": "L_OR_1"}),
        ("LA", "L", {"alpha_mode": "L_OR_1_FILL"}),
        xfail_unsupported_mode()("RGB", "L", {}),
        ("RGBA", "L", {"alpha_mode": "L"}),
        ("RGBA", "L", {"alpha_mode": "L_OR_1"}),
        ("RGBA", "L", {"alpha_mode": "L_OR_1_FILL"}),
        ("PLA", "L", {"alpha_mode": "L"}),
        ("PRGBA", "L", {"alpha_mode": "L"}),
        ("novel/RGBA_monochrome", "L", {"alpha_mode": "L"}),
        ("novel/RGBA_monochrome", "1", {"alpha_mode": "L_OR_1"}),
        ("novel/RGBA_monochrome", "1", {"alpha_mode": "L_OR_1_FILL"}),
    ],
    indirect=["alpha_splitter"],
)
def test_alpha_splitter(
    infile: str, expected_alpha_mode: str, alpha_splitter: AlphaSplitter
) -> None:
    infile = get_infile(infile)

    with temporary_filename(".png") as color_outfile:
        with temporary_filename(".png") as alpha_outfile:
            input_image = Image.open(infile)
            if input_image.mode == "P":
                expected_color_mode = remove_palette_from_image(
                    input_image
                ).mode.rstrip("A")
            else:
                expected_color_mode = input_image.mode.rstrip("A")

            alpha_splitter(infile, color=color_outfile, alpha=alpha_outfile)

            with Image.open(color_outfile) as color_image:
                assert color_image.mode == expected_color_mode
                assert color_image.size == input_image.size

            with Image.open(alpha_outfile) as alpha_image:
                assert alpha_image.mode == expected_alpha_mode
                assert alpha_image.size == input_image.size
