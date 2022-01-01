#!/usr/bin/env pwsh
# Script for creating a working conda environment on Windows

$ErrorActionPreference = "Stop"

conda deactivate
conda remove -y --name pipescaler --all
conda create -y --name pipescaler python=3.8
conda activate pipescaler

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
    pytest `
    pytest-cov `
    pytest-xdist `
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

pip install `
    numpy==1.20.3
