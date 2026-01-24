#  Copyright 2020-2026 Karl T Debiec. All rights reserved. This software may be modified
#  and distributed under the terms of the BSD license. See the LICENSE file for details.
"""Tests for ScaledPairIdentifier."""

from platform import system
from shutil import copy

import numpy as np
import pytest
from PIL import Image

from pipescaler.common.file import get_temp_directory_path, get_temp_file_path
from pipescaler.image import ScaledPairIdentifier
from pipescaler.testing.file import get_test_input_path


@pytest.mark.xfail(
    system() in {"Linux"}, raises=OSError, reason=f"Not supported on {system()}"
)
def test_review():
    with (
        get_temp_directory_path() as input_directory,
        get_temp_directory_path() as project_root,
    ):
        with (
            get_temp_file_path("csv") as hash_file,
            get_temp_file_path("csv") as pairs_file,
        ):
            # Copy basic input files and prepare scaled pairs
            for mode in ["L", "LA", "RGB", "RGBA"]:
                input_path = get_test_input_path(mode)
                output_path = (
                    input_directory / f"{input_path.stem}_1{input_path.suffix}"
                )
                copy(input_path, output_path)

                parent = Image.open(input_path)
                for scale in np.array([1 / (2**x) for x in range(1, 7)]):
                    width = round(parent.size[0] * scale)
                    height = round(parent.size[1] * scale)
                    if width < 8 or height < 8:
                        break
                    child = parent.resize(
                        (width, height),
                        Image.Resampling.NEAREST,  # type: ignore
                    )
                    output_path = (
                        input_directory
                        / f"{input_path.stem}_{scale}{input_path.suffix}"
                    )

                    child.save(output_path)

            # Copy alternate input files and prepare scaled pairs
            for mode in ["L", "LA", "RGB", "RGBA"]:
                input_path = get_test_input_path(f"alt/{mode}")
                output_path = (
                    input_directory / f"{input_path.stem}_alt_1{input_path.suffix}"
                )

                copy(input_path, output_path)

                parent = Image.open(input_path)
                for scale in np.array([1 / (2**x) for x in range(1, 7)]):
                    width = round(parent.size[0] * scale)
                    height = round(parent.size[1] * scale)
                    if width < 8 or height < 8:
                        break
                    child = parent.resize(
                        (width, height),
                        Image.Resampling.NEAREST,  # type: ignore
                    )
                    output_path = (
                        input_directory
                        / f"{input_path.stem}_alt_{scale}{input_path.suffix}"
                    )
                    child.save(output_path)

            scaled_pair_identifier = ScaledPairIdentifier(
                input_dir_path=input_directory,
                project_root=project_root,
                hash_file=hash_file,
                pairs_file=pairs_file,
                interactive=False,
            )
            scaled_pair_identifier.identify_pairs()
            scaled_pair_identifier.sync_scaled_directory()
            scaled_pair_identifier.sync_comparison_directory()
