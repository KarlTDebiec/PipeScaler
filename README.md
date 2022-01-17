[![Python: =3.8](https://img.shields.io/badge/python-3.8-green.svg)](https://docs.python.org/3/whatsnew/3.8.html)
[![Build Status](https://app.travis-ci.com/KarlTDebiec/PipeScaler.svg?branch=master)](https://app.travis-ci.com/github/KarlTDebiec/PipeScaler)
[![Coverage](https://img.shields.io/badge/coverage-76-yellowgreen)](https://app.travis-ci.com/github/KarlTDebiec/PipeScaler)
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
* [CitraSource](https://github.com/KarlTDebiec/PipeScaler/tree/master/pipescaler/sources/citra_source.py) - Yields images dumped by [Citra](https://citra-emu.org).
* [DirectorySource](https://github.com/KarlTDebiec/PipeScaler/tree/master/pipescaler/sources/directory_source.py) - Yields images from a directory.
* [DolphinSource](https://github.com/KarlTDebiec/PipeScaler/tree/master/pipescaler/sources/dolphin_source.py) - Yields images dumped by [Dolphin](https://dolphin-emu.org/).
* [TexmodSource](https://github.com/KarlTDebiec/PipeScaler/tree/master/pipescaler/sources/texmod_source.py) - Yields images dumped by [TexMod](https://www.moddb.com/downloads/texmod4).

**Processors** perform operations on an image, yielding a modified downstream image.
PipeScaler includes the following image processors:
* [AppleScriptExternalProcessor](https://github.com/KarlTDebiec/PipeScaler/tree/master/pipescaler/processors/apple_script_external_processor.py) - Runs image through an [AppleScript](https://developer.apple.com/library/archive/documentation/AppleScript/Conceptual/AppleScriptLangGuide/introduction/ASLR_intro.html); for example using [Pixelmator Pro](https://www.pixelmator.com/support/guide/pixelmator-pro/1270/).
* [AutomatorExternalProcessor](https://github.com/KarlTDebiec/PipeScaler/tree/master/pipescaler/processors/automator_external_processor.py) - Applies an [Automator QuickAction](https://support.apple.com/guide/automator/welcome/mac) to an image; for example using [Pixelmator Pro](https://www.pixelmator.com/support/guide/pixelmator-pro/1270/).
* [CropProcessor](https://github.com/KarlTDebiec/PipeScaler/tree/master/pipescaler/processors/crop_processor.py) - Crops image canvas.
* [ESRGANProcessor](https://github.com/KarlTDebiec/PipeScaler/tree/master/pipescaler/processors/esrgan_processor.py) - Upscales and/or denoises image using [ESRGAN](https://github.com/xinntao/ESRGAN); supports old and new architectures.
* [ExpandProcessor](https://github.com/KarlTDebiec/PipeScaler/tree/master/pipescaler/processors/expand_processor.py) - Expands image canvas.
* [GigapixelAiProcessor](https://github.com/KarlTDebiec/PipeScaler/tree/master/pipescaler/processors/gigapixel_ai_proessor.py) - Upscales image using [Gigapixel AI](https://www.topazlabs.com/gigapixel-ai).
* [HeightToNormalProcessor](https://github.com/KarlTDebiec/PipeScaler/tree/master/pipescaler/processors/height_to_normal_processor.py) - Converts height map image to a normal map image.
* [ModeProcessor](https://github.com/KarlTDebiec/PipeScaler/tree/master/pipescaler/processors/mode_processor.py) - Converts mode of image.
* [PngquantExternalProcessor](https://github.com/KarlTDebiec/PipeScaler/tree/master/pipescaler/processors/pngquant_external_processor.py) - Compresses image palette using [pngquant](https://pngquant.org/).
* [PotraceExternalProcessor](https://github.com/KarlTDebiec/PipeScaler/tree/master/pipescaler/processors/potrace_external_processor.py) - Traces image using [Potrace](http://potrace.sourceforge.net/) and re-rasterizes, optionally resizing.
* [ResizeProcessor](https://github.com/KarlTDebiec/PipeScaler/tree/master/pipescaler/processors/resize_processor.py) - Resizes image canvas using bicubic, bilinear, lanczos, or nearest-neighbor interpolation.
* [SideChannelProcessor](https://github.com/KarlTDebiec/PipeScaler/tree/master/pipescaler/processors/side_channel_processor.py) - Replaces image with an alternative sourced from a defined directory.
* [SolidColorProcessor](https://github.com/KarlTDebiec/PipeScaler/tree/master/pipescaler/processors/solid_color_processor.py) - Sets entire image color to its average color, optionally resizing.
* [TexconvExternalProcessor](https://github.com/KarlTDebiec/PipeScaler/tree/master/pipescaler/processors/texconv_external_processor.py) - Compresses image using [Texconv](https://github.com/Microsoft/DirectXTex/wiki/Texconv).
* [ThresholdProcessor](https://github.com/KarlTDebiec/PipeScaler/tree/master/pipescaler/processors/threshold_processor.py) - Converts image to black and white using threshold, optionally denoising.
* [WaifuExternalProcessor](https://github.com/KarlTDebiec/PipeScaler/tree/master/pipescaler/processors/waifu_external_processor.py) - Upscales and/or denoises image using [waifu2x](https://github.com/nagadomi/waifu2x).
* [WebProcessor](https://github.com/KarlTDebiec/PipeScaler/tree/master/pipescaler/processors/web_processor.py) - POSTs image to a defined URL, which responds with processed image.
* [XbrzProcessor](https://github.com/KarlTDebiec/PipeScaler/tree/master/pipescaler/processors/xbrz_processor.py) - Upscales image using [xbrz](https://github.com/ioistired/xbrz.py).

**Splitters** separate one image into two or more downstream images. PipeScaler includes the
following image splitters:
* [AlphaSplitter](https://github.com/KarlTDebiec/PipeScaler/tree/master/pipescaler/splitters/alpha_splitter.py) - Splits image with transparency into separate alpha and color images.
* [NormalSplitter](https://github.com/KarlTDebiec/PipeScaler/tree/master/pipescaler/splitters/normal_splitter.py) - Splits a normal map image into separate x, y, and z images.

**Mergers** combine two or more images into a single downstream image. PipeScaler includes
the following image mergers:
* [AlphaMerger](https://github.com/KarlTDebiec/PipeScaler/tree/master/pipescaler/mergers/alpha_merger.py) - Merges alpha and color images into a single image with transparency.
* [ColorMatchMerger](https://github.com/KarlTDebiec/PipeScaler/tree/master/pipescaler/mergers/color_match_merger.py) - Matches an image's color histogram to that of a reference image.
* [NormalMerger](https://github.com/KarlTDebiec/PipeScaler/tree/master/pipescaler/mergers/normal_merger.py) - Merges x, y, and z images into a single normal map image.

**Sorters** direct images through different downstream pipeline sections. PipeScaler
includes the following image sorters:
* [AlphaSorter](https://github.com/KarlTDebiec/PipeScaler/tree/master/pipescaler/sorters/alpha_sorter.py) - Sorts image based on presence and use of alpha channel.
* [GrayscaleSorter](https://github.com/KarlTDebiec/PipeScaler/tree/master/pipescaler/sorters/grayscale_sorter.py) - Sorts image based on presence and use of color channels.
* [ListSorter](https://github.com/KarlTDebiec/PipeScaler/tree/master/pipescaler/sorters/list_sorter.py) - Sorts image based on filename using a set of configured lists.
* [ModeSorter](https://github.com/KarlTDebiec/PipeScaler/tree/master/pipescaler/sorters/mode_sorter.py) - Sorts image based on mode.
* [RegexSorter](https://github.com/KarlTDebiec/PipeScaler/tree/master/pipescaler/sorters/regex_sorter.py) - Sorts image based on filename using a regular expression.
* [SizeSorter](https://github.com/KarlTDebiec/PipeScaler/tree/master/pipescaler/sorters/size_sorter.py) - Sorts image based on canvas size.
* [SolidColorSorter](https://github.com/KarlTDebiec/PipeScaler/tree/master/pipescaler/sorters/solid_color_sorter.py) - Sorts image based on presence of multiple colors.

**Termini** perform final operations on images. PipeScaler includes the following image
termini:
* [CopyFileTerminus](https://github.com/KarlTDebiec/PipeScaler/tree/master/pipescaler/termini/copy_file_terminus.py) - Copies images to a defined output directory.
