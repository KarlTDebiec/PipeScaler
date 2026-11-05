#  Copyright 2026 Karl T Debiec. All rights reserved. This software may be modified
#  and distributed under the terms of the BSD license. See the LICENSE file for details.
"""Generate text geometry references using the original Potrace 1.16 executable.

Run with `uv run python test/scripts/generate_potrace_reference.py`. The executable
is needed only to regenerate the fixture; the regression tests use libpotrace.
Corner-only traces let GeoJSON retain every vertex without approximating cubics.
"""

from __future__ import annotations

import json
import subprocess
import tempfile
from argparse import ArgumentParser
from pathlib import Path

import numpy as np
from PIL import Image

from pipescaler.common.cli.argument_parsing import get_arg_groups_by_name

__all__ = ["main"]


def main():
    """Write reference vertices for every turn policy on an ambiguous checkerboard.

    Raises:
        subprocess.CalledProcessError: if the reference executable fails
        OSError: if the reference executable or fixture files cannot be accessed
    """
    parser = ArgumentParser(description=__doc__)
    arg_groups = get_arg_groups_by_name(parser, "input arguments", "output arguments")

    # Input arguments
    arg_groups["input arguments"].add_argument(
        "--executable-path", type=Path, default=Path("potrace")
    )

    # Output arguments
    arg_groups["output arguments"].add_argument(
        "--output-path",
        type=Path,
        default=Path(__file__).resolve().parents[1]
        / "data"
        / "potrace"
        / "checkerboard.json",
    )
    arguments = parser.parse_args()
    pixels = np.full((8, 8), 255, dtype=np.uint8)
    pixels[1:7, 1:7] = np.indices((6, 6)).sum(axis=0) % 2 * 255
    paths = {}
    with tempfile.TemporaryDirectory() as temp_dir:
        input_path = Path(temp_dir) / "checkerboard.bmp"
        Image.fromarray(pixels).save(input_path)
        for policy in (
            "black",
            "white",
            "left",
            "right",
            "minority",
            "majority",
            "random",
        ):
            result = subprocess.run(
                [
                    str(arguments.executable_path),
                    str(input_path),
                    "--backend",
                    "geojson",
                    "--blacklevel",
                    "0.3",
                    "--turdsize",
                    "0",
                    "--alphamax",
                    "0",
                    "--turnpolicy",
                    policy,
                    "--unit",
                    "1000000",
                    "--output",
                    "-",
                ],
                capture_output=True,
                text=True,
                check=True,
            )
            paths[policy] = [
                ring
                for feature in json.loads(result.stdout)["features"]
                for ring in feature["geometry"]["coordinates"]
            ]
    arguments.output_path.parent.mkdir(parents=True, exist_ok=True)
    arguments.output_path.write_text(
        json.dumps(
            {
                "source": "Potrace 1.16 GeoJSON, unit=1000000, turdsize=0, alphamax=0",
                "pixels": pixels.tolist(),
                "paths": paths,
            },
            indent=2,
        )
        + "\n",
        encoding="utf-8",
    )


if __name__ == "__main__":
    main()
