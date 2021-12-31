[![Python: ≥3.8](https://img.shields.io/badge/python-≥3.8-green.svg)](https://docs.python.org/3/whatsnew/3.8.html)
[![Build Status](https://app.travis-ci.com/KarlTDebiec/PipeScaler.svg?branch=master)](https://app.travis-ci.com/github/KarlTDebiec/PipeScaler)
[![Coverage](https://img.shields.io/badge/coverage-77-yellowgreen)](https://app.travis-ci.com/github/KarlTDebiec/PipeScaler)
[![Code Style: black](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/psf/black)
[![License: BSD 3-Clause](https://img.shields.io/badge/license-BSD%203--Clause-blue.svg)](https://opensource.org/licenses/BSD-3-Clause)

PipeScaler is a package for processing collections of images with a focus on increasing
resolution. Users define a pipeline in which images flow from a source through a series
of sorters, processors, splitters, and mergers into a terminus. Intermediate images
along the pipeline are saved to allow processing to be tracked, stopped, and
resumed. Pipelines are straightforward to configure using yaml, including reusable
stages and blocks.

**Sources** feed images into the downstream pipeline. PipeScaler includes the following
image sources:
* [CitraSource](https://github.com/KarlTDebiec/PipeScaler/tree/master/lib/abc.py) - Yields images dumped by [Citra](https://citra-emu.org).
* [DirectorySource](https://github.com/KarlTDebiec/PipeScaler/tree/master/lib/abc.py) - Yields images from a directory.
* [DolphinSource](https://github.com/KarlTDebiec/PipeScaler/tree/master/lib/abc.py) - Yields images dumped by [Dolphin](https://dolphin-emu.org/).
* [TexmodSource](https://github.com/KarlTDebiec/PipeScaler/tree/master/lib/abc.py) - Yields images dumped by [TexMod](https://www.moddb.com/downloads/texmod4).

**Processors** perform operations on an image, yielding a modified downstream image.
PipeScaler includes the following image processors:
* [AppleScriptExternalProcessor](https://github.com/KarlTDebiec/PipeScaler/tree/master/lib/abc.py) - Runs image through an [AppleScript](https://developer.apple.com/library/archive/documentation/AppleScript/Conceptual/AppleScriptLangGuide/introduction/ASLR_intro.html); for example using [Pixelmator Pro](https://www.pixelmator.com/support/guide/pixelmator-pro/1270/).
* [AutomatorExternalProcessor](https://github.com/KarlTDebiec/PipeScaler/tree/master/lib/abc.py) - Applies an [Automator QuickAction](https://support.apple.com/guide/automator/welcome/mac) to an image; for example using [Pixelmator Pro](https://www.pixelmator.com/support/guide/pixelmator-pro/1270/).
* [CropProcessor](https://github.com/KarlTDebiec/PipeScaler/tree/master/lib/abc.py) - Crops image canvas.
* [ESRGANProcessor](https://github.com/KarlTDebiec/PipeScaler/tree/master/lib/abc.py) - Upscales and/or denoises image using [ESRGAN](https://github.com/xinntao/ESRGAN); supports old and new architectures..
* [ExpandProcessor](https://github.com/KarlTDebiec/PipeScaler/tree/master/lib/abc.py) - Expands image canvas.
* [HeightToNormalProcessor](https://github.com/KarlTDebiec/PipeScaler/tree/master/lib/abc.py) - Converts height map image to a normal map image.
* [ModeProcessor](https://github.com/KarlTDebiec/PipeScaler/tree/master/lib/abc.py) - Converts mode of image.
* [PngquantExternalProcessor](https://github.com/KarlTDebiec/PipeScaler/tree/master/lib/abc.py) - Compresses image palette using [pngquant](https://pngquant.org/).
* [PotraceExternalProcessor](https://github.com/KarlTDebiec/PipeScaler/tree/master/lib/abc.py) - Traces image using [Potrace](http://potrace.sourceforge.net/) and re-rasterizes, optionally resizing.
* [ResizeProcessor](https://github.com/KarlTDebiec/PipeScaler/tree/master/lib/abc.py) - Resizes image canvas using bicubic, bilinear, lanczos, or nearest-neighbor interpolation.
* [SideChannelProcessor](https://github.com/KarlTDebiec/PipeScaler/tree/master/lib/abc.py) - Replaces image with an alternative sourced from a defined directory.
* [SolidColorProcessor](https://github.com/KarlTDebiec/PipeScaler/tree/master/lib/abc.py) - Sets entire image color to its average color, optionally resizing.
* [TexconvExternalProcessor](https://github.com/KarlTDebiec/PipeScaler/tree/master/lib/abc.py) - Compresses image using [Texconv](https://github.com/Microsoft/DirectXTex/wiki/Texconv).
* [ThresholdProcessor](https://github.com/KarlTDebiec/PipeScaler/tree/master/lib/abc.py) - Converts image to black and white using threshold, optionally denoising.
* [WaifuExternalProcessor](https://github.com/KarlTDebiec/PipeScaler/tree/master/lib/abc.py) - Upscales and/or denoises image using [waifu2x](https://github.com/nagadomi/waifu2x).
* [WebProcessor](https://github.com/KarlTDebiec/PipeScaler/tree/master/lib/abc.py) - POSTs image to a defined URL, which responds with processed image.
* [XbrzProcessor](https://github.com/KarlTDebiec/PipeScaler/tree/master/lib/abc.py) - Upscales image using [xbrz](https://github.com/ioistired/xbrz.py).

**Splitters** separate one image into two or more downstream images. PipeScaler includes the
following image splitters:
* [AlphaSplitter](https://github.com/KarlTDebiec/PipeScaler/tree/master/lib/abc.py) - Splits image with transparency into separate alpha and color images.
* [NormalSplitter](https://github.com/KarlTDebiec/PipeScaler/tree/master/lib/abc.py) - Splits a normal map image into separate x, y, and z images.

**Mergers** combine two or more images into a single downstream image. PipeScaler includes
the following image mergers:
* [AlphaMerger](https://github.com/KarlTDebiec/PipeScaler/tree/master/lib/abc.py) - Merges alpha and color images into a single image with transparency.
* [ColorMatchMerger](https://github.com/KarlTDebiec/PipeScaler/tree/master/lib/abc.py) - Matches an image's color histogram to that of a reference image.
* [NormalMerger](https://github.com/KarlTDebiec/PipeScaler/tree/master/lib/abc.py) - Merges x, y, and z images into a single normal map image.

**Sorters** direct images through different downstream pipeline sections. PipeScaler
includes the following image sorters:
* [AlphaSorter](https://github.com/KarlTDebiec/PipeScaler/tree/master/lib/abc.py) - Sorts image based on presence and use of alpha channel.
* [GrayscaleSorter](https://github.com/KarlTDebiec/PipeScaler/tree/master/lib/abc.py) - Sorts image based on presence and use of color channels.
* [ListSorter](https://github.com/KarlTDebiec/PipeScaler/tree/master/lib/abc.py) - Sorts image based on filename using a set of configured lists.
* [ModeSorter](https://github.com/KarlTDebiec/PipeScaler/tree/master/lib/abc.py) - Sorts image based on mode.
* [RegexSorter](https://github.com/KarlTDebiec/PipeScaler/tree/master/lib/abc.py) - Sorts image based on filename using a regular expression.
* [SizeSorter](https://github.com/KarlTDebiec/PipeScaler/tree/master/lib/abc.py) - Sorts image based on canvas size.
* [SolidColorSorter](https://github.com/KarlTDebiec/PipeScaler/tree/master/lib/abc.py) - Sorts image based on presence of multiple colors.

**Termini** perform final operations on images. PipeScaler includes the following image
termini:
* [CopyFileTerminus](https://github.com/KarlTDebiec/PipeScaler/tree/master/lib/abc.py) - Copies images to a defined output directory.
