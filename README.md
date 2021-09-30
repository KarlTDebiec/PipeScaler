[![Python: ≥3.8](https://img.shields.io/badge/python-≥3.8-green.svg)](https://docs.python.org/3/whatsnew/3.8.html)
[![Build Status](https://app.travis-ci.com/KarlTDebiec/PipeScaler.svg?branch=master)](https://app.travis-ci.com/github/KarlTDebiec/PipeScaler)
[![Coverage](https://img.shields.io/badge/coverage-74-yellowgreen)](https://app.travis-ci.com/github/KarlTDebiec/PipeScaler)
[![Code Style: black](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/psf/black)
[![License: BSD 3-Clause](https://img.shields.io/badge/license-BSD%203--Clause-blue.svg)](https://opensource.org/licenses/BSD-3-Clause)

PipeScaler is a package for processing collections of images with a focus on improving
quality and increasing resolution. Users define a pipeline in which image flow from a
source through a series of sorters, processors, splitters, and mergers into a terminus.
Intermediate images along the pipeline are stored to allow processing to be tracked,
and stopped and resumed.

PipeScaler includes the following image sources:
* [CitraSource](https://github.com/KarlTDebiec/PipeScaler/tree/master/pipescaler/sources/citra_source.py) - Yields images dumped by [Citra](https://citra-emu.org).
* [DirectorySource](https://github.com/KarlTDebiec/PipeScaler/tree/master/pipescaler/sources/directory_source.py) - Yields images from a directory.
* [DolphinSource](https://github.com/KarlTDebiec/PipeScaler/tree/master/pipescaler/sources/dolphin_source.py) - Yields images dumped by [Dolphin](https://dolphin-emu.org/).
* [TexmodSource](https://github.com/KarlTDebiec/PipeScaler/tree/master/pipescaler/sources/texmod_source.py) - Yields images dumped by [TexMod](https://www.moddb.com/downloads/texmod4).

PipeScaler includes the following image processors:
* [AppleScriptProcessor](https://github.com/KarlTDebiec/PipeScaler/tree/master/pipescaler/processors/apple_script_processor.py)
* [AutomatorProcessor](https://github.com/KarlTDebiec/PipeScaler/tree/master/pipescaler/processors/automator_processor.py)
* [CropProcessor](https://github.com/KarlTDebiec/PipeScaler/tree/master/pipescaler/processors/crop_processor.py)
* [ESRGANProcessor](https://github.com/KarlTDebiec/PipeScaler/tree/master/pipescaler/processors/esrgan_processor.py) - Upscales and/or denoises using [ESRGAN](https://github.com/xinntao/ESRGAN).
* [ExpandProcessor](https://github.com/KarlTDebiec/PipeScaler/tree/master/pipescaler/processors/expand_processor.py)
* [HeightToNormalProcessor](https://github.com/KarlTDebiec/PipeScaler/tree/master/pipescaler/processors/height_to_normal_processor.py) - Converts a height map to a normal map.
* [ModeProcessor](https://github.com/KarlTDebiec/PipeScaler/tree/master/pipescaler/processors/mode_processor.py) - Converts mode between RGBA, RGB, LA, and L.
* [PotraceExternalProcessor](https://github.com/KarlTDebiec/PipeScaler/tree/master/pipescaler/processors/potrace_external_processor.py)
* [PngquantProcessor](https://github.com/KarlTDebiec/PipeScaler/tree/master/pipescaler/processors/pngquant_processor.py)
* [ResizeProcessor](https://github.com/KarlTDebiec/PipeScaler/tree/master/pipescaler/processors/resize_processor.py)
* [SideChannelProcessor](https://github.com/KarlTDebiec/PipeScaler/tree/master/pipescaler/processors/side_channel_processor.py)
* [SolidColorProcessor](https://github.com/KarlTDebiec/PipeScaler/tree/master/pipescaler/processors/solid_color_processor.py)
* [TexconvProcessor](https://github.com/KarlTDebiec/PipeScaler/tree/master/pipescaler/processors/texconv_processor.py) - Converts using [Texconv](https://github.com/microsoft/DirectXTex)
* [ThresholdProcessor](https://github.com/KarlTDebiec/PipeScaler/tree/master/pipescaler/processors/threshold_processor.py)
* [WaifuProcessor](https://github.com/KarlTDebiec/PipeScaler/tree/master/pipescaler/processors/waifu_processor.py) - Upscales and/or denoises using [waifu2x](https://github.com/nagadomi/waifu2x).
* [WaifuExternalProcessor](https://github.com/KarlTDebiec/PipeScaler/tree/master/pipescaler/processors/waifu_external_processor.py) - Upscales and/or denoises using [waifu2x](https://github.com/nagadomi/waifu2x).
* [XbrzProcessor](https://github.com/KarlTDebiec/PipeScaler/tree/master/pipescaler/processors/xbrz_processor.py) - Upscales using [xbrz](https://github.com/ioistired/xbrz.py).

PipeScaler includes the following image splitters:
* [AlphaSplitter](https://github.com/KarlTDebiec/PipeScaler/tree/master/pipescaler/splitters/alpha_splitter.py)
* [ColorToAlphaSplitter](https://github.com/KarlTDebiec/PipeScaler/tree/master/pipescaler/splitters/color_to_alpha_splitter.py)
* [NormalSplitter](https://github.com/KarlTDebiec/PipeScaler/tree/master/pipescaler/splitters/normal_splitter.py)

PipeScaler includes the following image mergers:
* [AlphaMerger](https://github.com/KarlTDebiec/PipeScaler/tree/master/pipescaler/mergers/alpha_merger.py)
* [ColorMatchMerger](https://github.com/KarlTDebiec/PipeScaler/tree/master/pipescaler/mergers/color_match_merger.py)
* [ColorToAlphaMerger](https://github.com/KarlTDebiec/PipeScaler/tree/master/pipescaler/mergers/color_to_alpha_merger.py)
* [NormalMerger](https://github.com/KarlTDebiec/PipeScaler/tree/master/pipescaler/mergers/normal_merger.py)

PipeScaler includes the following image sorters:
* [AlphaSorter](https://github.com/KarlTDebiec/PipeScaler/tree/master/pipescaler/sorters/alpha_sorter.py)
* [GrayscaleSorter](https://github.com/KarlTDebiec/PipeScaler/tree/master/pipescaler/sorters/grayscale_sorter.py)
* [ListSorter](https://github.com/KarlTDebiec/PipeScaler/tree/master/pipescaler/sorters/list_sorter.py)
* [ModeSorter](https://github.com/KarlTDebiec/PipeScaler/tree/master/pipescaler/sorters/mode_sorter.py)
* [RegexSorter](https://github.com/KarlTDebiec/PipeScaler/tree/master/pipescaler/sorters/regex_sorter.py)
* [SizeSorter](https://github.com/KarlTDebiec/PipeScaler/tree/master/pipescaler/sorters/size_sorter.py)
* [SolidColorSorter](https://github.com/KarlTDebiec/PipeScaler/tree/master/pipescaler/sorters/solid_color_sorter.py)

PipeScaler includes the following image termini:
* [CopyFileTerminus](https://github.com/KarlTDebiec/PipeScaler/tree/master/pipescaler/termini/copy_file_terminus.py)

