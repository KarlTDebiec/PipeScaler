#  Copyright 2026 Karl T Debiec. All rights reserved. This software may be modified
#  and distributed under the terms of the BSD license. See the LICENSE file for details.
"""Bind the stable libpotrace C ABI and copy traced curves into memory.

Requires an installed libpotrace shared library, such as `libpotrace0` on
Debian/Ubuntu. System library discovery is used by default. To override discovery,
set `PIPESCALER_POTRACE_LIBRARY` to an absolute `.so`, `.dylib`, or Windows DLL path.
The platform CI jobs in `.github/workflows/build.yml` contain the pinned-source
download, checksum verification, and shared-library compiler commands. For manual
builds, adapt their paths to local directories and use `cc` on Linux/macOS or an
x64 MSVC developer shell on Windows.

The structures mirror upstream `potracelib.h` from Potrace 1.16. In particular,
`potrace_word` is C unsigned long (32 bits on Windows, 64 on Unix), and pixels
are packed most-significant-bit first in bottom-up row order. No Python extension
or executable is used.
"""

from __future__ import annotations

import ctypes as ct
import os
from ctypes.util import find_library
from functools import cache

import numpy as np
from numpy.typing import NDArray
from reportlab.graphics.shapes import Path
from reportlab.lib.colors import black

__all__ = ["trace_bitmap"]


class _Bitmap(ct.Structure):
    """Native packed bitmap; storage remains owned by the calling Python frame."""

    _fields_ = [
        ("w", ct.c_int),
        ("h", ct.c_int),
        ("dy", ct.c_int),
        ("map", ct.POINTER(ct.c_ulong)),
    ]
    """Width, height, words per row, and pixel storage from potracelib.h."""


class _Point(ct.Structure):
    """Native double precision coordinate."""

    _fields_ = [("x", ct.c_double), ("y", ct.c_double)]
    """Horizontal and vertical coordinates."""


class _Curve(ct.Structure):
    """Native sequence of corner or cubic segments."""

    _fields_ = [
        ("n", ct.c_int),
        ("tag", ct.POINTER(ct.c_int)),
        ("c", ct.POINTER(_Point * 3)),
    ]
    """Segment count, segment tags, and three control points per segment."""


class _Path(ct.Structure):
    """Native linked path, including holes and nested islands."""


_Path._fields_ = [
    ("area", ct.c_int),
    ("sign", ct.c_int),
    ("curve", _Curve),
    ("next", ct.POINTER(_Path)),
    ("childlist", ct.POINTER(_Path)),
    ("sibling", ct.POINTER(_Path)),
    ("priv", ct.c_void_p),
]


class _Progress(ct.Structure):
    """Native progress callback configuration, left disabled."""

    _fields_ = [
        ("callback", ct.c_void_p),
        ("data", ct.c_void_p),
        ("min", ct.c_double),
        ("max", ct.c_double),
        ("epsilon", ct.c_double),
    ]
    """Callback, context, range, and granularity from potracelib.h."""


class _Params(ct.Structure):
    """Native tracing parameters."""

    _fields_ = [
        ("turdsize", ct.c_int),
        ("turnpolicy", ct.c_int),
        ("alphamax", ct.c_double),
        ("opticurve", ct.c_int),
        ("opttolerance", ct.c_double),
        ("progress", _Progress),
    ]
    """Algorithm settings followed by disabled progress reporting."""


class _State(ct.Structure):
    """Native trace result, freed after copying its curves."""

    _fields_ = [
        ("status", ct.c_int),
        ("plist", ct.POINTER(_Path)),
        ("priv", ct.c_void_p),
    ]
    """Completion status, linked paths, and opaque private state."""


def trace_bitmap(  # noqa: PLR0913
    bitmap: NDArray[np.bool_],
    *,
    turdsize: int,
    turnpolicy: int,
    alphamax: float,
    opticurve: bool,
    opttolerance: float,
) -> Path:
    """Trace black foreground pixels and return a compound vector path.

    Arguments:
        bitmap: top-down, two-dimensional array with True for black foreground pixels
        turdsize: maximum speckle area to suppress
        turnpolicy: native ambiguity policy code, from zero through six
        alphamax: corner smoothing threshold
        opticurve: whether to optimize cubic curves
        opttolerance: curve optimization tolerance in input pixels
    Returns:
        compound black path with even-odd filling, in bottom-left drawing coordinates
    Raises:
        OSError: if libpotrace is unavailable
        MemoryError: if the native tracer cannot allocate or complete its result
    """
    library = _import_libpotrace()
    height, width = bitmap.shape
    word_bytes = ct.sizeof(ct.c_ulong)
    word_bits = word_bytes * 8
    stride = (width + word_bits - 1) // word_bits
    # Match BMP scan order before tracing, including coordinate-dependent turn decisions
    padded = np.pad(bitmap[::-1], ((0, 0), (0, stride * word_bits - width)))
    packed = np.packbits(padded, axis=1, bitorder="big")
    words = np.ascontiguousarray(
        packed.view(np.dtype(f">u{word_bytes}")).astype(f"u{word_bytes}")
    )
    native_bitmap = _Bitmap(
        width, height, stride, words.ctypes.data_as(ct.POINTER(ct.c_ulong))
    )
    params = _Params(
        turdsize, turnpolicy, alphamax, int(opticurve), opttolerance, _Progress()
    )
    state = library.potrace_trace(ct.byref(params), ct.byref(native_bitmap))
    if not state:
        raise MemoryError("libpotrace could not allocate a trace result")
    try:
        if state.contents.status != 0:
            raise MemoryError("libpotrace returned an incomplete trace")
        output = Path(fillColor=black, strokeColor=None, fillMode=0)
        path = state.contents.plist
        while path:
            curve = path.contents.curve
            start = curve.c[curve.n - 1][2]
            output.moveTo(start.x, start.y)
            for index in range(curve.n):
                first, second, end = curve.c[index]
                if curve.tag[index] == 2:
                    output.lineTo(second.x, second.y)
                    output.lineTo(end.x, end.y)
                else:
                    output.curveTo(
                        first.x,
                        first.y,
                        second.x,
                        second.y,
                        end.x,
                        end.y,
                    )
            output.closePath()
            path = path.contents.next
        return output
    finally:
        library.potrace_state_free(state)


@cache
def _import_libpotrace() -> ct.CDLL:
    """Load and declare the native ABI once, when tracing is first requested.

    Returns:
        configured native library handle
    Raises:
        OSError: if no usable library is installed or explicitly configured
    """
    library_path = os.environ.get("PIPESCALER_POTRACE_LIBRARY") or find_library(
        "potrace"
    )
    if not library_path:
        raise OSError(
            "libpotrace is required: install its shared library and set "
            "PIPESCALER_POTRACE_LIBRARY if it is outside the system search path"
        )
    library = ct.CDLL(library_path)
    library.potrace_trace.argtypes = [ct.POINTER(_Params), ct.POINTER(_Bitmap)]
    library.potrace_trace.restype = ct.POINTER(_State)
    library.potrace_state_free.argtypes = [ct.POINTER(_State)]
    library.potrace_state_free.restype = None
    return library
