#!/usr/bin/env bash
# Script for creating a working conda environment on macOS,
# with the latest version of required packages

set -euo pipefail

conda deactivate || true
conda remove -y --name pipescaler --all || true
conda create -y --name pipescaler python=3.13
source "$(conda info --base)/etc/profile.d/conda.sh"
conda activate pipescaler

pip install \
    black \
    imagehash \
    ipython \
    isort \
    numba \
    numpy \
    opencv-python \
    pandas \
    pandas-stubs \
    pillow \
    pyright \
    pytest \
    pytest-cov \
    pytest-xdist \
    ruff \
    scikit-image \
    types-Pillow \
    uv

pip install \
    xbrz.py@git+https://github.com/ioistired/xbrz.py

conda install -y -c pytorch \
    pytorch
