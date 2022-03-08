#!/bin/bash -e
# Script for creating a working conda environment on macOS,
# with the latest version of required packages

source /usr/local/Caskroom/miniconda/base/etc/profile.d/conda.sh

conda deactivate
conda remove -y --name pipescaler --all
conda create -y --name pipescaler python=3.8
conda activate pipescaler

pip install \
    black \
    flask \
    imagehash \
    ipython \
    isort \
    numba \
    numpy \
    pandas \
    pillow \
    prospector \
    pytest \
    pytest-cov \
    pytest-xdist \
    pyyaml \
    requests \
    scikit-image \
    setuptools \
    svglib \
    watchdog \
    xbrz.py

conda install -y \
    pytables

conda install -y -c pytorch \
    pytorch \
    torchvision \
    torchaudio
