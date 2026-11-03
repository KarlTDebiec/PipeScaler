#  Copyright 2026 Karl T Debiec. All rights reserved. This software may be modified
#  and distributed under the terms of the BSD license. See the LICENSE file for details.
"""Verify that CI installs CPU-only PyTorch without CUDA runtime distributions."""

from __future__ import annotations

from importlib.metadata import distributions

import torch

__all__ = ["main"]


def main():
    """Reject CUDA, NVIDIA, and Triton packages and GPU PyTorch builds.

    Raises:
        RuntimeError: if CUDA runtime distributions or a GPU PyTorch build are installed
    """
    gpu_packages = sorted(
        distribution.name
        for distribution in distributions()
        if distribution.name.lower()
        .replace("_", "-")
        .startswith(("cuda", "nvidia", "triton", "pytorch-triton"))
    )
    if gpu_packages:
        raise RuntimeError(f"CUDA runtime distributions installed: {gpu_packages}")
    if torch.version.cuda is not None or torch.version.hip is not None:
        raise RuntimeError(f"Expected CPU-only PyTorch, found {torch.__version__}")
    print(
        f"CPU-only PyTorch {torch.__version__}; no CUDA runtime distributions installed"
    )


if __name__ == "__main__":
    main()
