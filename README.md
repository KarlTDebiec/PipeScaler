[![Python: =3.9](https://img.shields.io/badge/python-3.9-green.svg)](https://docs.python.org/3/whatsnew/3.9.html)
[![Build](https://github.com/KarlTDebiec/PipeScaler/actions/workflows/build.yml/badge.svg)](https://github.com/KarlTDebiec/PipeScaler/actions/workflows/build.yml)
[![Coverage](https://img.shields.io/badge/coverage-83-green)](https://github.com/KarlTDebiec/PipeScaler)
[![Code Style: black](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/psf/black)
[![License: BSD 3-Clause](https://img.shields.io/badge/license-BSD%203--Clause-blue.svg)](https://opensource.org/licenses/BSD-3-Clause)

PipeScaler is a package for processing collections of images with a focus on upscaling
resolution. Users define a pipeline in which images flow from a source through a series
of sorters, processors, splitters, and mergers into a terminus. Checkpoint images
along the pipeline may be saved to allow processing to be tracked, stopped, and
resumed.

**Sources** feed images into the downstream pipeline. PipeScaler includes the following
image sources:
* [DirectorySource](https://github.com/KarlTDebiec/PipeScaler/tree/master/pipescaler/pipelines/sources/directory_source.py) - Yields images from a directory.

**Processors** perform operations on an image, yielding a modified downstream image.
PipeScaler includes the following image processors:
* [AppleScriptProcessor](https://github.com/KarlTDebiec/PipeScaler/tree/master/pipescaler/image/processors/apple_script_processor.py) - Runs image through an [AppleScript](https://developer.apple.com/library/archive/documentation/AppleScript/Conceptual/AppleScriptLangGuide/introduction/ASLR_intro.html), using an application such as [Pixelmator Pro](https://www.pixelmator.com/support/guide/pixelmator-pro/1270/).
* [AutomatorProcessor](https://github.com/KarlTDebiec/PipeScaler/tree/master/pipescaler/image/processors/automator_processor.py) - Applies an [Automator QuickAction](https://support.apple.com/guide/automator/welcome/mac) to an image; for example using [Pixelmator Pro](https://www.pixelmator.com/support/guide/pixelmator-pro/1270/).
* [CropProcessor](https://github.com/KarlTDebiec/PipeScaler/tree/master/pipescaler/image/processors/crop_processor.py) - Crops image canvas.
* [EsrganProcessor](https://github.com/KarlTDebiec/PipeScaler/tree/master/pipescaler/image/processors/esrgan_processor.py) - Upscales and/or denoises image using [ESRGAN](https://github.com/xinntao/ESRGAN) via PyTorch.
* [ExpandProcessor](https://github.com/KarlTDebiec/PipeScaler/tree/master/pipescaler/image/processors/expand_processor.py) - Expands image canvas by mirroring image around edges.
* [HeightToNormalProcessor](https://github.com/KarlTDebiec/PipeScaler/tree/master/pipescaler/image/processors/height_to_normal_processor.py) - Converts height map image to a normal map image.
* [ModeProcessor](https://github.com/KarlTDebiec/PipeScaler/tree/master/pipescaler/image/processors/mode_processor.py) - Converts mode of image.
* [PotraceProcessor](https://github.com/KarlTDebiec/PipeScaler/tree/master/pipescaler/image/processors/potrace_processor.py) - Traces image using [Potrace](http://potrace.sourceforge.net/) and re-rasterizes, optionally resizing.
* [ResizeProcessor](https://github.com/KarlTDebiec/PipeScaler/tree/master/pipescaler/image/processors/resize_processor.py) - Resizes image canvas.
* [SharpenProcessor](https://github.com/KarlTDebiec/PipeScaler/tree/master/pipescaler/image/processors/sharpen_processor.py) - Sharpens an image.
* [SolidColorProcessor](https://github.com/KarlTDebiec/PipeScaler/tree/master/pipescaler/image/processors/solid_color_processor.py) - Sets entire image color to its average color, optionally resizing.
* [ThresholdProcessor](https://github.com/KarlTDebiec/PipeScaler/tree/master/pipescaler/image/processors/threshold_processor.py) - Converts image to black and white using threshold, optionally denoising.
* [WaifuExternalProcessor](https://github.com/KarlTDebiec/PipeScaler/tree/master/pipescaler/image/processors/waifu_external_processor.py) - Upscales and/or denoises image using [Waifu2x](https://github.com/nagadomi/waifu2x) via an external executable.
* [WaifuProcessor](https://github.com/KarlTDebiec/PipeScaler/tree/master/pipescaler/image/processors/waifu_processor.py) - Upscales and/or denoises image using [Waifu2x](https://github.com/nagadomi/waifu2x) via PyTorch.
* [WebProcessor](https://github.com/KarlTDebiec/PipeScaler/tree/master/pipescaler/image/processors/web_processor.py) - POSTs image to a defined URL, which responds with processed image.
* [XbrzProcessor](https://github.com/KarlTDebiec/PipeScaler/tree/master/pipescaler/image/processors/xbrz_processor.py) - Upscales image using [xbrz](https://github.com/ioistired/xbrz.py).

**Splitters** separate one image into two or more downstream images. PipeScaler includes
the following image splitters:
* [AlphaSplitter](https://github.com/KarlTDebiec/PipeScaler/tree/master/pipescaler/image/splitters/alpha_splitter.py) - Splits image with transparency into separate color and alpha images.
* [NormalSplitter](https://github.com/KarlTDebiec/PipeScaler/tree/master/pipescaler/image/splitters/normal_splitter.py) - Splits a normal map image into separate x, y, and z images.

**Mergers** combine two or more images into a single downstream image. PipeScaler
includes the following image mergers:
* [AlphaMerger](https://github.com/KarlTDebiec/PipeScaler/tree/master/pipescaler/image/mergers/alpha_merger.py) - Merges color and alpha images into a single image with transparency.
* [HistogramMatchMerger](https://github.com/KarlTDebiec/PipeScaler/tree/master/pipescaler/image/mergers/histogram_match_merger.py) - Matches an image's color histogram to that of a reference image.
* [NormalMerger](https://github.com/KarlTDebiec/PipeScaler/tree/master/pipescaler/image/mergers/normal_merger.py) - Merges x, y, and z images into a single normal map image.
* [PaletteMatchMerger](https://github.com/KarlTDebiec/PipeScaler/tree/master/pipescaler/image/mergers/palette_match_merger.py) - Matches an image's color palette to that of a reference image.

**Sorters** classify images, allowing them to be directed  through different downstream
pipeline sections. PipeScaler includes the following image sorters:
* [AlphaSorter](https://github.com/KarlTDebiec/PipeScaler/tree/master/pipescaler/pipelines/sorters/alpha_sorter.py) - Sorts image based on presence and use of alpha channel.
* [GrayscaleSorter](https://github.com/KarlTDebiec/PipeScaler/tree/master/pipescaler/pipelines/sorters/grayscale_sorter.py) - Sorts image based on presence and use of color channels.
* [ListSorter](https://github.com/KarlTDebiec/PipeScaler/tree/master/pipescaler/pipelines/sorters/list_sorter.py) - Sorts image based on filename using a set of configured lists.
* [ModeSorter](https://github.com/KarlTDebiec/PipeScaler/tree/master/pipescaler/pipelines/sorters/mode_sorter.py) - Sorts image based on mode.
* [MonochromeSorter](https://github.com/KarlTDebiec/PipeScaler/tree/master/pipescaler/pipelines/sorters/monochrome_sorter.py) - Sorts image based on presence and use of colors other than black and white.
* [RegexSorter](https://github.com/KarlTDebiec/PipeScaler/tree/master/pipescaler/pipelines/sorters/regex_sorter.py) - Sorts image based on filename using a regular expression.
* [SizeSorter](https://github.com/KarlTDebiec/PipeScaler/tree/master/pipescaler/pipelines/sorters/size_sorter.py) - Sorts image based on canvas size.
* [SolidColorSorter](https://github.com/KarlTDebiec/PipeScaler/tree/master/pipescaler/pipelines/sorters/solid_color_sorter.py) - Sorts image based on whether their entire canvas is a solid color.

**Termini** perform final operations on images. PipeScaler includes the following image
termini:
* [CopyFileTerminus](https://github.com/KarlTDebiec/PipeScaler/tree/master/pipescaler/pipelines/termini/copy_file_terminus.py) - Copies images to a defined output directory.
