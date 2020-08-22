#!/bin/bash -ex

TEST_ROOT="${TRAVIS_BUILD_DIR}/test/"

cd ${TEST_ROOT}
tar cv htmlcov | xz -9 > htmlcov.txz
base64 htmlcov.txz | tee htmlcov.txz.b64

