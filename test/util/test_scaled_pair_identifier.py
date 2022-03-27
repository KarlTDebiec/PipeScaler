#!/usr/bin/env python
#   Copyright (C) 2020-2022 Karl T Debiec
#   All rights reserved. This software may be modified and distributed under
#   the terms of the BSD license. See the LICENSE file for details.
"""Tests for ScaledPairIdentifier"""
from os.path import basename, join, splitext
from platform import system
from shutil import copy
from tempfile import TemporaryDirectory

import numpy as np
import pytest
from PIL import Image

from pipescaler.common import temporary_filename
from pipescaler.core import get_files
from pipescaler.testing import get_infile
from pipescaler.util import ScaledPairIdentifier


@pytest.mark.xfail(
    system() in {"Linux"}, raises=OSError, reason=f"Not supported on {system()}"
)
def test_review() -> None:
    with TemporaryDirectory() as input_directory:
        for mode in ["L", "LA", "RGB", "RGBA"]:
            base_filename = splitext(basename(get_infile(mode)))[0]
            copy(get_infile(mode), join(input_directory, f"{base_filename}_1.png"))
            parent = Image.open(get_infile(mode))
            for scale in np.array([1 / (2**x) for x in range(1, 7)]):
                width = round(parent.size[0] * scale)
                height = round(parent.size[1] * scale)
                if width < 8 or height < 8:
                    break
                child = parent.resize((width, height), Image.NEAREST)
                outfile = join(
                    input_directory,
                    f"{splitext(basename(get_infile(mode)))[0]}_{scale}_1.png",
                )
                child.save(outfile)
        for mode in ["L", "LA", "RGB", "RGBA"]:
            base_filename = splitext(basename(get_infile(f"alt/{mode}")))[0]
            copy(
                get_infile(f"alt/{mode}"),
                join(input_directory, f"{base_filename}_alt_1.png"),
            )
            parent = Image.open(get_infile(f"alt/{mode}"))
            for scale in np.array([1 / (2**x) for x in range(1, 7)]):
                width = round(parent.size[0] * scale)
                height = round(parent.size[1] * scale)
                if width < 8 or height < 8:
                    break
                child = parent.resize((width, height), Image.NEAREST)
                outfile = join(
                    input_directory,
                    f"{splitext(basename(get_infile(f'alt/{mode}')))[0]}_alt_{scale}_1.png",
                )
                child.save(outfile)
        absolute_filenames = get_files(input_directory, style="absolute")
        absolute_filenames = sorted(list(absolute_filenames))
        filenames = {splitext(basename(f))[0]: f for f in absolute_filenames}

        with temporary_filename(".csv") as pairs_file:
            with temporary_filename(".csv") as hash_file:
                with TemporaryDirectory() as image_directory:
                    scaled_pair_identifier = ScaledPairIdentifier(
                        filenames=filenames,
                        pairs_file=pairs_file,
                        hash_file=hash_file,
                        image_directory=image_directory,
                        interactive=False,
                    )
                    scaled_pair_identifier.identify_pairs()
