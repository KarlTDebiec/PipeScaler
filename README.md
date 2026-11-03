[![Python: =3.14](https://img.shields.io/badge/python-3.14-green.svg)](https://docs.python.org/3/whatsnew/3.14.html)
[![Build](https://github.com/KarlTDebiec/PipeScaler/actions/workflows/build.yml/badge.svg)](https://github.com/KarlTDebiec/PipeScaler/actions/workflows/build.yml)
[![Coverage](https://img.shields.io/badge/coverage-83-green)](https://github.com/KarlTDebiec/PipeScaler)
[![Code Style: Ruff](https://img.shields.io/badge/code%20style-Ruff-D7FF64.svg)](https://docs.astral.sh/ruff/)
[![License: BSD 3-Clause](https://img.shields.io/badge/license-BSD%203--Clause-blue.svg)](https://opensource.org/licenses/BSD-3-Clause)

PipeScaler is a package for processing collections of files with a focus on upscaling
image and video resolution. Users define a pipeline in which objects flow from a source
through a series of sorters, processors, splitters, and mergers into a terminus.
Checkpoints along the pipeline may be saved to allow processing to be tracked, stopped,
and resumed.

Developer guidance: [Architecture](docs/ARCHITECTURE.md),
[Code Style](docs/STYLE.md), [Documentation](docs/DOCUMENTATION.md), and
[Contributing](docs/CONTRIBUTING.md).

Other packages can add commands through [CLI extensions](docs/CLI_EXTENSIONS.md).

# Native tracing library

`PotraceProcessor` uses `libpotrace` directly; the Potrace executable is unnecessary.
Install a system shared library (for example, `libpotrace0` on Debian/Ubuntu), or
build the pinned library with a C compiler:

```sh
uv run --no-project python scripts/build_libpotrace.py .native
export PIPESCALER_POTRACE_LIBRARY="$PWD/.native/libpotrace.so"
```

On macOS the output is `.native/libpotrace.dylib`. On Windows, run the build from
an x64 MSVC developer shell and set
`$env:PIPESCALER_POTRACE_LIBRARY = (Resolve-Path .native/potrace.dll).Path`.
The environment variable overrides system library discovery. The build verifies
the upstream source checksum and compiles only the library. Potrace's upstream
license applies to that separately installed library.

Tracing uses keyword settings such as `PotraceProcessor(blacklevel=0.3,
alphamax=1.34, opttolerance=0.2, scale=2)`; executable argument tokens are removed.

# Image Processing

PipeScaler includes the following components for image processing:

**Sources** yield images for downstream modification:
* [ImageDirectorySource](https://github.com/KarlTDebiec/PipeScaler/tree/master/pipescaler/image/pipelines/sources/image_directory_source.py) - Yields images from a directory.
* [ImageVideoFrameSource](https://github.com/KarlTDebiec/PipeScaler/tree/master/pipescaler/image/pipelines/sources/image_video_frame_source.py) - Yields images from a video file.
* [ImageZipSource](https://github.com/KarlTDebiec/PipeScaler/tree/master/pipescaler/image/pipelines/sources/image_zip_source.py) - Yields images from a ZIP archive.

**Processors** perform operations on an image, yielding a modified image:
* [CropProcessor](https://github.com/KarlTDebiec/PipeScaler/tree/master/pipescaler/image/operators/processors/crop_processor.py) - Crops image canvas.
* [ExpandProcessor](https://github.com/KarlTDebiec/PipeScaler/tree/master/pipescaler/image/operators/processors/expand_processor.py) - Expands image canvas by mirroring image around edges.
* [HeightToNormalProcessor](https://github.com/KarlTDebiec/PipeScaler/tree/master/pipescaler/image/operators/processors/height_to_normal_processor.py) - Converts height map image to a normal map image.
* [ImagequantProcessor](https://github.com/KarlTDebiec/PipeScaler/tree/master/pipescaler/image/operators/processors/imagequant_processor.py) - Reduces image palettes using libimagequant.
* [ModeProcessor](https://github.com/KarlTDebiec/PipeScaler/tree/master/pipescaler/image/operators/processors/mode_processor.py) - Converts mode of image.
* [PotraceProcessor](https://github.com/KarlTDebiec/PipeScaler/tree/master/pipescaler/image/operators/processors/potrace_processor.py) - Traces image using [Potrace](http://potrace.sourceforge.net/) and re-rasterizes, optionally resizing.
* [ResizeProcessor](https://github.com/KarlTDebiec/PipeScaler/tree/master/pipescaler/image/operators/processors/resize_processor.py) - Resizes image canvas.
* [SharpenProcessor](https://github.com/KarlTDebiec/PipeScaler/tree/master/pipescaler/image/operators/processors/sharpen_processor.py) - Sharpens an image.
* [SolidColorProcessor](https://github.com/KarlTDebiec/PipeScaler/tree/master/pipescaler/image/operators/processors/solid_color_processor.py) - Sets entire image color to its average color, optionally resizing.
* [ThresholdProcessor](https://github.com/KarlTDebiec/PipeScaler/tree/master/pipescaler/image/operators/processors/threshold_processor.py) - Converts image to black and white using threshold, optionally denoising.
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
* [ImageZipTerminus](https://github.com/KarlTDebiec/PipeScaler/tree/master/pipescaler/image/pipelines/termini/image_zip_terminus.py) - Collects images into a ZIP archive.

# Video Processing

PipeScaler includes the following components for video processing:

**Sources** yield videos for downstream modification:
* [VideoDirectorySource](https://github.com/KarlTDebiec/PipeScaler/tree/master/pipescaler/video/pipelines/sources/video_directory_source.py) - Yields videos from a directory.

**Sorters** classify videos, allowing them to be routed through different operations:
* [VideoAspectRatioSorter](https://github.com/KarlTDebiec/PipeScaler/tree/master/pipescaler/video/pipelines/sorters/video_aspect_ratio_sorter.py) - Sorts video based on aspect ratio.

**Termini** collect processed videos:
* [VideoDirectoryTerminus](https://github.com/KarlTDebiec/PipeScaler/tree/master/pipescaler/video/pipelines/termini/video_directory_terminus.py) - Copies videos to an output directory.
