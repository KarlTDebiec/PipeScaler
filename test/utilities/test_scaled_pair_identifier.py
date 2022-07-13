#!/usr/bin/env python
#  Copyright 2020-2022 Karl T Debiec
#  All rights reserved. This software may be modified and distributed under
#  the terms of the BSD license. See the LICENSE file for details.
"""Tests for ScaledPairIdentifier."""
from platform import system
from shutil import copy

import numpy as np
import pytest
from PIL import Image

from pipescaler.common import get_temp_directory_path, get_temp_file_path
from pipescaler.testing import get_test_infile_path
from pipescaler.utilities import ScaledPairIdentifier


@pytest.mark.xfail(
    system() in {"Linux"}, raises=OSError, reason=f"Not supported on {system()}"
)
def test_review() -> None:
    with get_temp_directory_path() as input_directory, get_temp_directory_path() as project_root:
        with get_temp_file_path("csv") as hash_file, get_temp_file_path(
            "csv"
        ) as pairs_file:

            # Copy basic infiles and prepare scaled pairs
            for mode in ["L", "LA", "RGB", "RGBA"]:
                infile = get_test_infile_path(mode)
                outfile = input_directory.joinpath(f"{infile.stem}_1{infile.suffix}")
                copy(infile, outfile)

                parent = Image.open(infile)
                for scale in np.array([1 / (2**x) for x in range(1, 7)]):
                    width = round(parent.size[0] * scale)
                    height = round(parent.size[1] * scale)
                    if width < 8 or height < 8:
                        break
                    child = parent.resize(
                        (width, height), Image.Resampling.NEAREST  # type: ignore
                    )
                    outfile = input_directory.joinpath(
                        f"{infile.stem}_{scale}{infile.suffix}"
                    )
                    child.save(outfile)

            # Copy alternate infiles and prepare scaled pairs
            for mode in ["L", "LA", "RGB", "RGBA"]:
                infile = get_test_infile_path(f"alt/{mode}")
                outfile = input_directory.joinpath(
                    f"{infile.stem}_alt_1{infile.suffix}"
                )
                copy(infile, outfile)

                parent = Image.open(infile)
                for scale in np.array([1 / (2**x) for x in range(1, 7)]):
                    width = round(parent.size[0] * scale)
                    height = round(parent.size[1] * scale)
                    if width < 8 or height < 8:
                        break
                    child = parent.resize(
                        (width, height), Image.Resampling.NEAREST  # type: ignore
                    )
                    outfile = input_directory.joinpath(
                        f"{infile.stem}_alt_{scale}{infile.suffix}"
                    )
                    child.save(outfile)

            scaled_pair_identifier = ScaledPairIdentifier(
                input_directories=input_directory,
                project_root=project_root,
                hash_file=hash_file,
                pairs_file=pairs_file,
                interactive=False,
            )
            scaled_pair_identifier.identify_pairs()
            scaled_pair_identifier.sync_scaled_directory()
            scaled_pair_identifier.sync_comparison_directory()
