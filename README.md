[![Build Status](https://travis-ci.org/KarlTDebiec/PipeScaler.svg?branch=master)](https://travis-ci.org/KarlTDebiec/PipeScaler)
[![Coverage Status](https://coveralls.io/repos/github/KarlTDebiec/PipeScaler/badge.svg?branch=master&service=github)](https://coveralls.io/github/KarlTDebiec/PipeScaler?branch=master)
[![Code style: black](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/psf/black)

PipeScaler is a tool for increasing the resolution of collections of images. It
wraps around tools including ESRGAN, Pixelmator, potrace, pngquant, waifu, and
xbrz, and allows them to be applied in a defined sequence to a collection of
images. Pipescaler supports directing images down different pipelines based on
their contents, filenames, or inclusion on configured lists.

Pipescaler may be used with any collection of images, and is currently
optimized for working with texture images dumped by Citra or TexMod.
