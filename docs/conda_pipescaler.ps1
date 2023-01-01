#!/usr/bin/env pwsh
# Script for creating a working conda environment on Windows,
# with the latest version of required packages

$ErrorActionPreference = "Stop"

conda deactivate
conda remove -y --name pipescaler --all
conda create -y --name pipescaler python=3.9
conda activate pipescaler

conda install -y `
    brotlipy

pip install `
    black `
    imagehash `
    ipython `
    isort `
    mypy `
    numba `
    numpy `
    pandas `
    pandas-stubs `
    pillow `
    prospector `
    pytest `
    pytest-cov `
    pytest-xdist `
    scikit-image `
    setuptools `
    svglib `
    types-Pillow `
    xbrz.py

conda install -y -c pytorch -c nvidia `
    pytorch `
    pytorch-cuda=11.7
