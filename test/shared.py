#!/usr/bin/env python
#   shared.py
#
#   Copyright (C) 2020-2021 Karl T Debiec
#   All rights reserved.
#
#   This software may be modified and distributed under the terms of the
#   BSD license. See the LICENSE file for details.
####################################### MODULES ########################################
from functools import partial
from os import getcwd
from os.path import dirname, join, splitext

import pytest

from pipescaler.processors import (
    AppleScriptProcessor,
    AutomatorProcessor,
    CropProcessor,
    ESRGANProcessor,
    ExpandProcessor,
    HeightToNormalProcessor,
    ModeProcessor,
    PngquantProcessor,
    ResizeProcessor,
    SideChannelProcessor,
    SolidColorProcessor,
    TexconvProcessor,
    WaifuExternalProcessor,
    WaifuProcessor,
    XbrzProcessor,
)
from pipescaler.common import package_root
from pipescaler.core import UnsupportedImageModeError

###################################### VARIABLES #######################################

alt_infiles = {
    splitext(f[-1])[0]: join(dirname(package_root), "test", "data", "infiles", "alt", f)
    for f in [
        "L.png",
        "LA.png",
        "PL.png",
        "PLA.png",
        "PRGB.png",
        "PRGBA.png",
        "RGB.png",
        "RGBA.png",
    ]
}
esrgan = {
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
        ("novel", "PRGB_magenta.png"),
        ("novel", "PRGB_normal.png"),
        ("novel", "RGB_magenta.png"),
        ("novel", "RGB_normal.png"),
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
scripts = {
    f: join(package_root, "scripts", f)
    for f in [
        "apng_creator.py",
        "directory_watcher.py",
        "pipe_runner.py",
        "scaled_image_identifier.py",
    ]
}

xfail_assertion = partial(pytest.param, marks=pytest.mark.xfail(raises=AssertionError))
xfail_unsupported_mode = partial(
    pytest.param, marks=pytest.mark.xfail(raises=UnsupportedImageModeError)
)


####################################### FIXTURES #######################################
@pytest.fixture(params=infiles.keys())
def infile(request):
    return infiles[request.param]


@pytest.fixture(
    params=[
        AppleScriptProcessor,
        AutomatorProcessor,
        CropProcessor,
        ESRGANProcessor,
        ExpandProcessor,
        HeightToNormalProcessor,
        ModeProcessor,
        PngquantProcessor,
        ResizeProcessor,
        SideChannelProcessor,
        SolidColorProcessor,
        TexconvProcessor,
        WaifuProcessor,
        WaifuExternalProcessor,
        XbrzProcessor,
    ]
)
def processor(request):
    return request.param


@pytest.fixture(params=scripts.keys())
def script(request):
    return scripts[request.param]
