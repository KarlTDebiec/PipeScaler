[![Python: =3.13](https://img.shields.io/badge/python-3.13-green.svg)](https://docs.python.org/3/whatsnew/3.13.html)
[![Build](https://github.com/KarlTDebiec/PipeScaler/actions/workflows/build.yml/badge.svg)](https://github.com/KarlTDebiec/PipeScaler/actions/workflows/build.yml)
[![Coverage](https://img.shields.io/badge/coverage-83-green)](https://github.com/KarlTDebiec/PipeScaler)
[![Code Style: black](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/psf/black)
[![License: BSD 3-Clause](https://img.shields.io/badge/license-BSD%203--Clause-blue.svg)](https://opensource.org/licenses/BSD-3-Clause)

PipeScaler is a package for processing collections of files with a focus on upscaling
image and video resolution. Users define a pipeline in which objects flow from a source
through a series of sorters, processors, splitters, and mergers into a terminus.
Checkpoints along the pipeline may be saved to allow processing to be tracked, stopped,
and resumed.

# Image Processing

PipeScaler includes the following components for image processing:

**Sources** yield images for downstream modification:
* [ImageDirectorySource](https://github.com/KarlTDebiec/PipeScaler/tree/master/pipescaler/image/pipelines/sources/image_directory_source.py) - Yields images from a directory.
* [ImageVideoFrameSource](https://github.com/KarlTDebiec/PipeScaler/tree/master/pipescaler/image/pipelines/sources/image_video_frame_source.py) - Yields images from a video file.

**Processors** perform operations on an image, yielding a modified image:
* [CropProcessor](https://github.com/KarlTDebiec/PipeScaler/tree/master/pipescaler/image/operators/processors/crop_processor.py) - Crops image canvas.
* [EsrganProcessor](https://github.com/KarlTDebiec/PipeScaler/tree/master/pipescaler/image/operators/processors/esrgan_processor.py) - Upscales and/or denoises image using [ESRGAN](https://github.com/xinntao/ESRGAN) via PyTorch.
* [ExpandProcessor](https://github.com/KarlTDebiec/PipeScaler/tree/master/pipescaler/image/operators/processors/expand_processor.py) - Expands image canvas by mirroring image around edges.
* [HeightToNormalProcessor](https://github.com/KarlTDebiec/PipeScaler/tree/master/pipescaler/image/operators/processors/height_to_normal_processor.py) - Converts height map image to a normal map image.
* [ModeProcessor](https://github.com/KarlTDebiec/PipeScaler/tree/master/pipescaler/image/operators/processors/mode_processor.py) - Converts mode of image.
* [PotraceProcessor](https://github.com/KarlTDebiec/PipeScaler/tree/master/pipescaler/image/operators/processors/potrace_processor.py) - Traces image using [Potrace](http://potrace.sourceforge.net/) and re-rasterizes, optionally resizing.
* [ResizeProcessor](https://github.com/KarlTDebiec/PipeScaler/tree/master/pipescaler/image/operators/processors/resize_processor.py) - Resizes image canvas.
* [SharpenProcessor](https://github.com/KarlTDebiec/PipeScaler/tree/master/pipescaler/image/operators/processors/sharpen_processor.py) - Sharpens an image.
* [SolidColorProcessor](https://github.com/KarlTDebiec/PipeScaler/tree/master/pipescaler/image/operators/processors/solid_color_processor.py) - Sets entire image color to its average color, optionally resizing.
* [ThresholdProcessor](https://github.com/KarlTDebiec/PipeScaler/tree/master/pipescaler/image/operators/processors/threshold_processor.py) - Converts image to black and white using threshold, optionally denoising.
* [WaifuProcessor](https://github.com/KarlTDebiec/PipeScaler/tree/master/pipescaler/image/operators/processors/waifu_processor.py) - Upscales and/or denoises image using [Waifu2x](https://github.com/nagadomi/waifu2x) via PyTorch.
* [XbrzProcessor](https://github.com/KarlTDebiec/PipeScaler/tree/master/pipescaler/image/operators/processors/xbrz_processor.py) - Upscales image using [xbrz](https://github.com/ioistired/xbrz.py).

**Splitters** separate one image into two or more images:
* [AlphaSplitter](https://github.com/KarlTDebiec/PipeScaler/tree/master/pipescaler/image/operators/splitters/alpha_splitter.py) - Splits image with transparency into separate color and alpha images.
* [NormalSplitter](https://github.com/KarlTDebiec/PipeScaler/tree/master/pipescaler/image/operators/splitters/normal_splitter.py) - Splits a normal map image into separate x, y, and z images.

**Mergers** combine two or more images into a single image:
* [AlphaMerger](https://github.com/KarlTDebiec/PipeScaler/tree/master/pipescaler/image/operators/mergers/alpha_merger.py) - Merges color and alpha images into a single image with transparency.
* [HistogramMatchMerger](https://github.com/KarlTDebiec/PipeScaler/tree/master/pipescaler/image/operators/mergers/histogram_match_merger.py) - Matches an image's color histogram to that of a reference image.
* [NormalMerger](https://github.com/KarlTDebiec/PipeScaler/tree/master/pipescaler/image/operators/mergers/normal_merger.py) - Merges x, y, and z images into a single normal map image.
* [PaletteMatchMerger](https://github.com/KarlTDebiec/PipeScaler/tree/master/pipescaler/image/operators/mergers/palette_match_merger.py) - Matches an image's color palette to that of a reference image.

**Sorters** classify images, allowing them to be routed through different operations:
* [AlphaSorter](https://github.com/KarlTDebiec/PipeScaler/tree/master/pipescaler/image/pipelines/sorters/alpha_sorter.py) - Sorts image based on presence and use of alpha channel.
* [GrayscaleSorter](https://github.com/KarlTDebiec/PipeScaler/tree/master/pipescaler/image/pipelines/sorters/grayscale_sorter.py) - Sorts image based on presence and use of color channels.
* [ModeSorter](https://github.com/KarlTDebiec/PipeScaler/tree/master/pipescaler/image/pipelines/sorters/mode_sorter.py) - Sorts image based on mode.
* [MonochromeSorter](https://github.com/KarlTDebiec/PipeScaler/tree/master/pipescaler/image/pipelines/sorters/monochrome_sorter.py) - Sorts image based on presence and use of colors other than black and white.
* [SizeSorter](https://github.com/KarlTDebiec/PipeScaler/tree/master/pipescaler/image/pipelines/sorters/size_sorter.py) - Sorts image based on canvas size.
* [SolidColorSorter](https://github.com/KarlTDebiec/PipeScaler/tree/master/pipescaler/image/pipelines/sorters/solid_color_sorter.py) - Sorts images based on whether their entire canvas is a solid color.

**Termini** collect processed images:
* [ImageDirectoryTerminus](https://github.com/KarlTDebiec/PipeScaler/tree/master/pipescaler/image/pipelines/termini/image_directory_terminus.py) - Copies images to an output directory.

# Video Processing

PipeScaler includes the following components for video processing:

**Sources** yield videos for downstream modification:
* [VideoDirectorySource](https://github.com/KarlTDebiec/PipeScaler/tree/master/pipescaler/video/pipelines/sources/video_directory_source.py) - Yields videos from a directory.

**Sorters** classify videos, allowing them to be routed through different operations:
* [VideoAspectRatioSorter](https://github.com/KarlTDebiec/PipeScaler/tree/master/pipescaler/video/pipelines/sorters/video_aspect_ratio_sorter.py) - Sorts video based on aspect ratio.

**Termini** collect processed videos:
* [VideoDirectoryTerminus](https://github.com/KarlTDebiec/PipeScaler/tree/master/pipescaler/video/pipelines/termini/video_directory_terminus.py) - Copies videos to an output directory.
