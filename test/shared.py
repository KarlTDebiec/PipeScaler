#!/usr/bin/env python
#   shared.py
#
#   Copyright (C) 2020-2021 Karl T Debiec
#   All rights reserved.
#
#   This software may be modified and distributed under the terms of the
#   BSD license. See the LICENSE file for details.
""""""
from functools import partial
from os import getcwd
from os.path import dirname, join, splitext

import pytest
from PIL import Image

from pipescaler.common import package_root
from pipescaler.core import UnsupportedImageModeError, remove_palette_from_image

alt_infiles = {
    splitext(f)[0]: join(dirname(package_root), "test", "data", "infiles", "alt", f)
    for f in [
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
    f[:-4]: join(getcwd(), "data", "models", f)
    for f in ["1x_BC1-smooth2.pth", "RRDB_ESRGAN_x4.pth", "RRDB_ESRGAN_x4_old_arch.pth"]
}
infiles = {
    splitext(f[-1])[0]: join(dirname(package_root), "test", "data", "infiles", *f)
    for f in [
        ("basic", "L.png"),
        ("basic", "LA.png"),
        ("basic", "PL.png"),
        ("basic", "PLA.png"),
        ("basic", "PRGB.png"),
        ("basic", "PRGBA.png"),
        ("basic", "RGB.png"),
        ("basic", "RGBA.png"),
        ("extra", "L_LA.png"),
        ("extra", "RGB_RGBA.png"),
        ("novel", "L_solid.png"),
        ("novel", "LA_solid.png"),
        ("novel", "RGB_magenta.png"),
        ("novel", "RGB_normal.png"),
        ("novel", "RGB_solid.png"),
        ("novel", "RGBA_solid.png"),
        ("novel", "PL_solid.png"),
        ("novel", "PLA_solid.png"),
        ("novel", "PRGB_magenta.png"),
        ("novel", "PRGB_normal.png"),
        ("novel", "PRGB_solid.png"),
        ("novel", "PRGBA_solid.png"),
        ("split", "LA_alpha_L.png"),
        ("split", "LA_alpha_PL.png"),
        ("split", "LA_color_L.png"),
        ("split", "LA_color_PL.png"),
        ("split", "RGB_magenta_alpha_L.png"),
        ("split", "RGB_magenta_alpha_PL.png"),
        ("split", "RGB_magenta_color_PRGB.png"),
        ("split", "RGB_magenta_color_RGB.png"),
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
scripts = {
    f: join(package_root, "scripts", f)
    for f in [
        "apng_creator.py",
        "directory_watcher.py",
        "pipe_runner.py",
        "scaled_image_identifier.py",
    ]
}


def expected_output_mode(input_image: Image.Image):
    if input_image.mode == "P":
        return remove_palette_from_image(input_image).mode
    else:
        return input_image.mode


xfail_assertion = partial(pytest.param, marks=pytest.mark.xfail(raises=AssertionError))
xfail_unsupported_mode = partial(
    pytest.param, marks=pytest.mark.xfail(raises=UnsupportedImageModeError)
)
xfail_value = partial(pytest.param, marks=pytest.mark.xfail(raises=ValueError))


@pytest.fixture(params=infiles.keys())
def infile(request):
    return infiles[request.param]


@pytest.fixture(params=scripts.keys())
def script(request):
    return scripts[request.param]
