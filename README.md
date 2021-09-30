[![Python: ≥3.8](https://img.shields.io/badge/python-≥3.8-green.svg)](https://docs.python.org/3/whatsnew/3.8.html)
[![Build Status](https://app.travis-ci.com/KarlTDebiec/PipeScaler.svg?branch=master)](https://app.travis-ci.com/github/KarlTDebiec/PipeScaler)
[![Coverage](https://img.shields.io/badge/coverage-74-yellowgreen)](https://app.travis-ci.com/github/KarlTDebiec/PipeScaler)
[![Code Style: black](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/psf/black)
[![License: BSD 3-Clause](https://img.shields.io/badge/license-BSD%203--Clause-blue.svg)](https://opensource.org/licenses/BSD-3-Clause)

PipeScaler is a package for processing collections of images with a focus on improving
quality and increasing resolution. Users define a pipeline in which images flow from a
source through a series of sorters, processors, splitters, and mergers into a terminus.
Intermediate images along the pipeline are stored to allow processing to be tracked,
and stopped and resumed. Pipelines are configured using yaml, including reusable stages
and blocks of stages.

Sources feed images sequentially into the downstream pipeline. PipeScaler includes the
following image sources:
* [CitraSource](https://github.com/KarlTDebiec/PipeScaler/tree/master/pipescaler/sources/citra_source.py) - Yields images dumped by [Citra](https://citra-emu.org).
* [DirectorySource](https://github.com/KarlTDebiec/PipeScaler/tree/master/pipescaler/sources/directory_source.py) - Yields images from a directory.
* [DolphinSource](https://github.com/KarlTDebiec/PipeScaler/tree/master/pipescaler/sources/dolphin_source.py) - Yields images dumped by [Dolphin](https://dolphin-emu.org/).
* [TexmodSource](https://github.com/KarlTDebiec/PipeScaler/tree/master/pipescaler/sources/texmod_source.py) - Yields images dumped by [TexMod](https://www.moddb.com/downloads/texmod4).

Processors perform operations to an image, yielding a modified downstream image.
PipeScaler includes the following image processors:
* [AppleScriptProcessor](https://github.com/KarlTDebiec/PipeScaler/tree/master/pipescaler/processors/apple_script_processor.py) - Runs through an [AppleScript](https://developer.apple.com/library/archive/documentation/AppleScript/Conceptual/AppleScriptLangGuide/introduction/ASLR_intro.html); for example using [Pixelmator Pro](https://www.pixelmator.com/support/guide/pixelmator-pro/1270/).
* [AutomatorProcessor](https://github.com/KarlTDebiec/PipeScaler/tree/master/pipescaler/processors/automator_processor.py) - Runs through an [Automator QuickAction](https://support.apple.com/guide/automator/welcome/mac); for example using [Pixelmator Pro](https://www.pixelmator.com/support/guide/pixelmator-pro/1270/).
* [CropProcessor](https://github.com/KarlTDebiec/PipeScaler/tree/master/pipescaler/processors/crop_processor.py) - Crops canvas.
* [ESRGANProcessor](https://github.com/KarlTDebiec/PipeScaler/tree/master/pipescaler/processors/esrgan_processor.py) - Upscales and/or denoises using [ESRGAN](https://github.com/xinntao/ESRGAN).
* [ExpandProcessor](https://github.com/KarlTDebiec/PipeScaler/tree/master/pipescaler/processors/expand_processor.py) - Expands canvas.
* [HeightToNormalProcessor](https://github.com/KarlTDebiec/PipeScaler/tree/master/pipescaler/processors/height_to_normal_processor.py) - Converts a height map to a normal map.
* [ModeProcessor](https://github.com/KarlTDebiec/PipeScaler/tree/master/pipescaler/processors/mode_processor.py) - Converts mode.
* [PotraceExternalProcessor](https://github.com/KarlTDebiec/PipeScaler/tree/master/pipescaler/processors/potrace_external_processor.py) - Traces using [Potrace](http://potrace.sourceforge.net/) and re-rasterizes, optionally resizing.
* [PngquantExternalProcessor](https://github.com/KarlTDebiec/PipeScaler/tree/master/pipescaler/processors/pngquant_external_processor.py) - Compresses palette using [pngquant](https://pngquant.org/).
* [ResizeProcessor](https://github.com/KarlTDebiec/PipeScaler/tree/master/pipescaler/processors/resize_processor.py) - Resizes canvas.
* [SideChannelProcessor](https://github.com/KarlTDebiec/PipeScaler/tree/master/pipescaler/processors/side_channel_processor.py) - Replaces image with an alternative from a directory.
* [SolidColorProcessor](https://github.com/KarlTDebiec/PipeScaler/tree/master/pipescaler/processors/solid_color_processor.py) - Sets entire canvas to its average color, optionally resizing.
* [TexconvProcessor](https://github.com/KarlTDebiec/PipeScaler/tree/master/pipescaler/processors/texconv_processor.py) - Compresses to DDS format using [Texconv](https://github.com/microsoft/DirectXTex)
* [ThresholdProcessor](https://github.com/KarlTDebiec/PipeScaler/tree/master/pipescaler/processors/threshold_processor.py) - Converts to black and white using threshold, optionally denoising.
* [WaifuProcessor](https://github.com/KarlTDebiec/PipeScaler/tree/master/pipescaler/processors/waifu_processor.py) - Upscales and/or denoises using [waifu2x](https://github.com/nagadomi/waifu2x).
* [WaifuExternalProcessor](https://github.com/KarlTDebiec/PipeScaler/tree/master/pipescaler/processors/waifu_external_processor.py) - Upscales and/or denoises using [waifu2x](https://github.com/nagadomi/waifu2x).
* [XbrzProcessor](https://github.com/KarlTDebiec/PipeScaler/tree/master/pipescaler/processors/xbrz_processor.py) - Upscales using [xbrz](https://github.com/ioistired/xbrz.py).

Splitters separate one image into two or more downstream images. PipeScaler includes the
following image splitters:
* [AlphaSplitter](https://github.com/KarlTDebiec/PipeScaler/tree/master/pipescaler/splitters/alpha_splitter.py) - Splits alpha and color channels.
* [ColorToAlphaSplitter](https://github.com/KarlTDebiec/PipeScaler/tree/master/pipescaler/splitters/color_to_alpha_splitter.py) - Splits alpha and color channels, treating a defined color as transparent.
* [NormalSplitter](https://github.com/KarlTDebiec/PipeScaler/tree/master/pipescaler/splitters/normal_splitter.py) - Splits a normal map into x, y, and z channels.

Mergers combine two or more images into a downstream single image. PipeScaler includes
the following image mergers:
* [AlphaMerger](https://github.com/KarlTDebiec/PipeScaler/tree/master/pipescaler/mergers/alpha_merger.py) - Merges alpha and color channels.
* [ColorMatchMerger](https://github.com/KarlTDebiec/PipeScaler/tree/master/pipescaler/mergers/color_match_merger.py) - Matches color histogram to a reference image.
* [ColorToAlphaMerger](https://github.com/KarlTDebiec/PipeScaler/tree/master/pipescaler/mergers/color_to_alpha_merger.py) - Merges alpha and color channels, treating a defined color as transparent.
* [NormalMerger](https://github.com/KarlTDebiec/PipeScaler/tree/master/pipescaler/mergers/normal_merger.py) - Merges x, y, and z channels into a normal map.

Sorters direct images through different sections of a pipeline. PipeScaler includes the
following image sorters:
* [AlphaSorter](https://github.com/KarlTDebiec/PipeScaler/tree/master/pipescaler/sorters/alpha_sorter.py) - Sorts by presence and use of alpha channel.
* [GrayscaleSorter](https://github.com/KarlTDebiec/PipeScaler/tree/master/pipescaler/sorters/grayscale_sorter.py) - Sorts by presence and use of color.
* [ListSorter](https://github.com/KarlTDebiec/PipeScaler/tree/master/pipescaler/sorters/list_sorter.py) - Sorts based on filename using a set of configured lists.
* [ModeSorter](https://github.com/KarlTDebiec/PipeScaler/tree/master/pipescaler/sorters/mode_sorter.py) - Sorts based on mode.
* [RegexSorter](https://github.com/KarlTDebiec/PipeScaler/tree/master/pipescaler/sorters/regex_sorter.py) - Sorts based on filename using a regular expression.
* [SizeSorter](https://github.com/KarlTDebiec/PipeScaler/tree/master/pipescaler/sorters/size_sorter.py) - Sorts based on canvas size.
* [SolidColorSorter](https://github.com/KarlTDebiec/PipeScaler/tree/master/pipescaler/sorters/solid_color_sorter.py) - Sorts based on presence of multiple colors.

Termini perform final operations on images. PipeScaler includes the following image
termini:
* [CopyFileTerminus](https://github.com/KarlTDebiec/PipeScaler/tree/master/pipescaler/termini/copy_file_terminus.py) - Copies files to an output directory.
