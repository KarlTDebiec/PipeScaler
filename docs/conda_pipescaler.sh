#!/bin/bash -e
# Script for creating a working conda environment on macOS,
# with the latest version of required packages

source /usr/local/Caskroom/miniconda/base/etc/profile.d/conda.sh

conda deactivate
conda remove -y --name pipescaler --all
conda create -y --name pipescaler python=3.11
conda activate pipescaler

conda install -y \
    brotlipy

pip install \
    black \
    imagehash \
    ipython \
    isort \
    mypy \
    numba \
    numpy \
    opencv-python \
    pandas \
    pandas-stubs \
    pillow \
    prospector \
    pytest \
    pytest-cov \
    pytest-xdist \
    scikit-image \
    setuptools \
    svglib \
    types-Pillow
pip install \
    xbrz.py@git+https://github.com/ioistired/xbrz.py

conda install -y -c pytorch \
    pytorch
