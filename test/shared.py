#!/usr/bin/env python
#   shared.py
#
#   Copyright (C) 2020-2022 Karl T Debiec
#   All rights reserved.
#
#   This software may be modified and distributed under the terms of the
#   BSD license. See the LICENSE file for details.
from os import environ, getenv
from os.path import dirname, join, splitext

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
