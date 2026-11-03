#  Copyright 2026 Karl T Debiec. All rights reserved. This software may be modified
#  and distributed under the terms of the BSD license. See the LICENSE file for details.
"""Build only the pinned upstream Potrace shared library, without its executables.

Requires a C compiler (`cc`, or MSVC `cl` in a developer shell on Windows).
Run with `uv run python scripts/build_libpotrace.py OUTPUT_DIRECTORY`, then set
`PIPESCALER_POTRACE_LIBRARY` to the printed absolute library path. Upstream sources
are downloaded into a temporary directory and verified before compilation.
"""

from __future__ import annotations

import hashlib
import io
import subprocess
import sys
import tarfile
import tempfile
import urllib.request
from pathlib import Path

__all__ = ["build_libpotrace"]


def build_libpotrace(output_dir_path: Path) -> Path:
    """Download verified upstream sources and compile the native library.

    Arguments:
        output_dir_path: directory in which to place the shared library
    Returns:
        absolute path of the compiled library
    Raises:
        ValueError: if the upstream archive checksum does not match
        subprocess.CalledProcessError: if compilation fails
    """
    output_dir_path = output_dir_path.resolve()
    output_dir_path.mkdir(parents=True, exist_ok=True)
    with urllib.request.urlopen(
        "https://potrace.sourceforge.net/download/1.16/potrace-1.16.tar.gz",
        timeout=60,
    ) as response:
        archive = response.read()
    if hashlib.sha256(archive).hexdigest() != (
        "be8248a17dedd6ccbaab2fcc45835bb0502d062e40fbded3bc56028ce5eb7acc"
    ):
        raise ValueError("Potrace source archive checksum mismatch")
    with tempfile.TemporaryDirectory() as temp_dir:
        with tarfile.open(fileobj=io.BytesIO(archive)) as source:
            source.extractall(temp_dir, filter="data")
        source_dir_path = Path(temp_dir) / "potrace-1.16" / "src"
        sources = ["curve.c", "trace.c", "decompose.c", "potracelib.c"]
        if sys.platform == "win32":
            library_path = output_dir_path / "potrace.dll"
            command = [
                "cl",
                "/nologo",
                "/O2",
                "/LD",
                "/std:c11",
                "/DHAVE_INTTYPES_H",
                '/DVERSION="1.16"',
                *sources,
                "/link",
                f"/OUT:{library_path}",
                "/EXPORT:potrace_trace",
                "/EXPORT:potrace_state_free",
            ]
        else:
            library_path = output_dir_path / (
                "libpotrace.dylib" if sys.platform == "darwin" else "libpotrace.so"
            )
            command = [
                "cc",
                "-O2",
                "-fPIC",
                "-DHAVE_INTTYPES_H",
                "-dynamiclib" if sys.platform == "darwin" else "-shared",
                '-DVERSION="1.16"',
                *sources,
                "-lm",
                "-o",
                str(library_path),
            ]
        subprocess.run(command, cwd=source_dir_path, check=True, stdout=sys.stderr)
    return library_path


if __name__ == "__main__":
    print(build_libpotrace(Path(sys.argv[1])))
