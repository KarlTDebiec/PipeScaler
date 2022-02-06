#!/usr/bin/env python
#   shared.py
#
#   Copyright (C) 2020-2022 Karl T Debiec
#   All rights reserved.
#
#   This software may be modified and distributed under the terms of the
#   BSD license. See the LICENSE file for details.
from functools import partial
from os import environ, getenv
from os.path import dirname, join, splitext
from platform import system
from typing import Set, Type

import pytest
from PIL import Image

from pipescaler.common import UnsupportedPlatformError
from pipescaler.core import UnsupportedImageModeError, remove_palette_from_image

if environ.get("PACKAGE_ROOT") is not None:
    package_root = getenv("PACKAGE_ROOT")
else:
    from pipescaler.common import package_root

alt_infiles = {
    splitext(f)[0]: join(dirname(package_root), "test", "data", "infiles", "alt", f)
    for f in [
        "1.png",
        "L.png",
        "LA.png",
        "RGB.png",
        "RGBA.png",
        "PL.png",
        "PLA.png",
        "PRGB.png",
        "PRGBA.png",
    ]
}
esrgan_models = {
    f[:-4]: join(dirname(package_root), "test", "data", "models", "ESRGAN", f)
    for f in ["1x_BC1-smooth2.pth", "RRDB_ESRGAN_x4.pth", "RRDB_ESRGAN_x4_old_arch.pth"]
}
waifu_models = {
    f[:-4]: join(dirname(package_root), "test", "data", "models", f)
    for f in ["WaifuUpConv7/a-2-3.pth", "WaifuVgg7/a-1-3.pth"]
}
infiles = {
    splitext(f[-1])[0]: join(dirname(package_root), "test", "data", "infiles", *f)
    for f in [
        ("basic", "1.png"),
        ("basic", "L.png"),
        ("basic", "LA.png"),
        ("basic", "PL.png"),
        ("basic", "PLA.png"),
        ("basic", "PRGB.png"),
        ("basic", "PRGBA.png"),
        ("basic", "RGB.png"),
        ("basic", "RGBA.png"),
        ("extra", "1_L.png"),
        ("extra", "L_LA.png"),
        ("extra", "RGB_RGBA.png"),
        ("novel", "L_solid.png"),
        ("novel", "LA_solid.png"),
        ("novel", "RGB_normal.png"),
        ("novel", "RGB_solid.png"),
        ("novel", "RGBA_solid.png"),
        ("novel", "PL_solid.png"),
        ("novel", "PLA_solid.png"),
        ("novel", "PRGB_normal.png"),
        ("novel", "PRGB_solid.png"),
        ("novel", "PRGBA_solid.png"),
        ("split", "LA_alpha_L.png"),
        ("split", "LA_alpha_PL.png"),
        ("split", "LA_color_L.png"),
        ("split", "LA_color_PL.png"),
        ("split", "RGB_normal_x_L.png"),
        ("split", "RGB_normal_x_PL.png"),
        ("split", "RGB_normal_y_L.png"),
        ("split", "RGB_normal_y_PL.png"),
        ("split", "RGB_normal_z_L.png"),
        ("split", "RGB_normal_z_PL.png"),
        ("split", "RGBA_alpha_L.png"),
        ("split", "RGBA_alpha_PL.png"),
        ("split", "RGBA_color_PRGB.png"),
        ("split", "RGBA_color_RGB.png"),
    ]
}
infile_subfolders = {
    subfolder: join(dirname(package_root), "test", "data", "infiles", subfolder)
    for subfolder in ["basic", "extra", "novel", "split"]
}


@pytest.fixture(params=infiles.keys())
def infile(request):
    return infiles[request.param]


def expected_output_mode(input_image: Image.Image):
    if input_image.mode == "P":
        return remove_palette_from_image(input_image).mode
    else:
        return input_image.mode


def skip_if_ci(inner=None):
    marks = [
        pytest.mark.skipif(
            getenv("CI") is not None,
            reason="Skip when running in CI",
        )
    ]
    if inner is not None:
        marks.append(inner.keywords["marks"].mark)

    return partial(pytest.param, marks=marks)


def xfail_if_platform(
    unsupported_platforms: Set[str] = None,
    raises: Type[Exception] = UnsupportedPlatformError,
):
    return partial(
        pytest.param,
        marks=pytest.mark.xfail(
            system() in unsupported_platforms,
            raises=raises,
            reason=f"Not supported on {system()}",
        ),
    )


def xfail_file_not_found():
    return partial(pytest.param, marks=pytest.mark.xfail(raises=FileNotFoundError))


def xfail_unsupported_mode():
    return partial(
        pytest.param, marks=pytest.mark.xfail(raises=UnsupportedImageModeError)
    )


def xfail_value():
    return partial(pytest.param, marks=pytest.mark.xfail(raises=ValueError))
