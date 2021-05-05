[![Python: ≥3.7](https://img.shields.io/badge/python-≥3.7-green.svg)](https://docs.python.org/3/whatsnew/3.7.html)
[![Build Status](https://travis-ci.org/KarlTDebiec/PipeScaler.svg?branch=master)](https://travis-ci.org/KarlTDebiec/PipeScaler)
[![Coverage Status](https://coveralls.io/repos/github/KarlTDebiec/PipeScaler/badge.svg?branch=master&service=github)](https://coveralls.io/github/KarlTDebiec/PipeScaler?branch=master)
[![Code Style: black](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/psf/black)
[![License: BSD 3-Clause](https://img.shields.io/badge/license-BSD%203--Clause-blue.svg)](https://opensource.org/licenses/BSD-3-Clause)

PipeScaler is a package for processing collections of images with a focus on increasing
resolution. Users define a pipeline of image sorters, processors, splitters, and mergers
to apply different operations to images in a collection depending on their contents.
Pipescaler has integrated support for [ESRGAN](https://github.com/xinntao/ESRGAN) (both
old and new architectures) and wraps around the external tools
[Pixelmator](https://www.pixelmator.com/pro/),
[potrace](http://potrace.sourceforge.net),
[pngquant](http://potrace.sourceforge.net),
[waifu2x](https://github.com/nagadomi/waifu2x), and
[xbrzcale](https://github.com/atheros/xbrzscale).

Pipescaler may be used with any collection of images, and is currently optimized for
working with texture images dumped by [Citra](https://citra-emu.org) and
[TexMod](https://www.moddb.com/downloads/texmod4).
