#!/usr/bin/env pwsh
# Script for creating a working conda environment on Windows,
# with the latest version of required packages

$ErrorActionPreference = "Stop"

conda deactivate
conda remove -y --name pipescaler --all
conda create -y --name pipescaler python=3.13
conda activate pipescaler

conda install -y `
    brotlipy
if(!$?) { Exit $LASTEXITCODE }

pip install `
    black `
    imagehash `
    ipython `
    isort `
    numba `
    numpy `
    opencv-python `
    pandas `
    pandas-stubs `
    pillow `
    prospector `
    pyright `
    pytest `
    pytest-cov `
    pytest-xdist `
    rlpycairo `
    scikit-image `
    svglib `
    types-Pillow
if(!$?) { Exit $LASTEXITCODE }

pip install `
    xbrz.py@git+https://github.com/ioistired/xbrz.py
if(!$?) { Exit $LASTEXITCODE }

conda install -y -c pytorch -c nvidia `
    pytorch `
    pytorch-cuda=11.8
if(!$?) { Exit $LASTEXITCODE }
