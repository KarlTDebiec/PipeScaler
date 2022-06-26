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
    flask `
    imagehash `
    ipython `
    isort `
    numba `
    numpy `
    pandas `
    pillow `
    prospector `
    pytest `
    pytest-cov `
    pytest-xdist `
    pytest-asyncio `
    pywinauto `
    pyyaml `
    requests `
    scikit-image `
    setuptools `
    svglib `
    watchdog `
    xbrz.py

conda install -y `
    pywin32

conda install -y -c pytorch `
    cudatoolkit=11.3 `
    pytorch `
    torchvision `
    torchaudio

