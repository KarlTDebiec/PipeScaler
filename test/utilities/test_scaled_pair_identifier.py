#!/usr/bin/env python
#  Copyright (C) 2020-2022. Karl T Debiec
#  All rights reserved. This software may be modified and distributed under
#  the terms of the BSD license. See the LICENSE file for details.
"""Tests for ScaledPairIdentifier."""
from pathlib import Path
from platform import system
from shutil import copy
from tempfile import TemporaryDirectory

import numpy as np
import pytest
from PIL import Image

from pipescaler.common import temporary_filename
from pipescaler.testing import get_infile
from pipescaler.utilities import ScaledPairIdentifier


@pytest.mark.xfail(
    system() in {"Linux"}, raises=OSError, reason=f"Not supported on {system()}"
)
def test_review() -> None:
    with TemporaryDirectory() as input_directory:
        input_directory = Path(input_directory)

        # Copy basic infiles and prepare scaled pairs
        for mode in ["L", "LA", "RGB", "RGBA"]:
            infile = get_infile(mode)
            outfile = input_directory.joinpath(f"{infile.stem}_1{infile.suffix}")
            copy(infile, outfile)

            parent = Image.open(infile)
            for scale in np.array([1 / (2**x) for x in range(1, 7)]):
                width = round(parent.size[0] * scale)
                height = round(parent.size[1] * scale)
                if width < 8 or height < 8:
                    break
                child = parent.resize((width, height), Image.Resampling.NEAREST)
                outfile = input_directory.joinpath(
                    f"{infile.stem}_{scale}{infile.suffix}"
                )
                child.save(outfile)

        # Copy alternate infiles and prepare scaled pairs
        for mode in ["L", "LA", "RGB", "RGBA"]:
            infile = get_infile(f"alt/{mode}")
            outfile = input_directory.joinpath(f"{infile.stem}_alt_1{infile.suffix}")
            copy(infile, outfile)

            parent = Image.open(infile)
            for scale in np.array([1 / (2**x) for x in range(1, 7)]):
                width = round(parent.size[0] * scale)
                height = round(parent.size[1] * scale)
                if width < 8 or height < 8:
                    break
                child = parent.resize((width, height), Image.Resampling.NEAREST)
                outfile = input_directory.joinpath(
                    f"{infile.stem}_alt_{scale}{infile.suffix}"
                )
                child.save(outfile)

        filenames = {filename.stem: filename for filename in input_directory.iterdir()}
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
