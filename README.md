[![Python: =3.13](https://img.shields.io/badge/python-3.13-green.svg)](https://docs.python.org/3/whatsnew/3.13.html)
[![Build](https://github.com/KarlTDebiec/PipeScaler/actions/workflows/build.yml/badge.svg)](https://github.com/KarlTDebiec/PipeScaler/actions/workflows/build.yml)
[![Code Style: Ruff](https://img.shields.io/badge/code%20style-Ruff-D7FF64.svg)](https://docs.astral.sh/ruff/)
[![License: BSD 3-Clause](https://img.shields.io/badge/license-BSD%203--Clause-blue.svg)](https://opensource.org/licenses/BSD-3-Clause)

PipeScaler processes collections of image and video files through composable
pipelines. Objects flow from sources through sorters, processors, splitters, and
mergers into termini. Checkpoints allow long-running pipelines to resume.

## Install from source

Use Python 3.13 and [uv](https://docs.astral.sh/uv/getting-started/installation/).
From a clone of this repository, install the package and its locked dependencies:

```console
uv sync --frozen
uv run pipescaler --help
```

The current package installs its image, video, and model dependencies together;
there are no optional extras. The example below uses Pillow resizing and requires
no model download or external executable. Some other operations require tools on
`PATH`: Potrace for tracing, apngasm for animated PNG assembly, pngquant for PNG
quantization, and Windows texconv for DDS operations. SVG rasterization also needs
Cairo. The [build workflow](.github/workflows/build.yml) records the system package
setup used by CI; install the tools required by the operations you choose.

## Resize one image

Generate an input image, then run the resize command from the repository root:

```console
uv run python -c "from PIL import Image; Image.new('RGB', (16, 16), 'coral').save('example.png')"
uv run pipescaler image process resize example.png example-2x.png --scale 2 --resample nearest
```

The result is a 32-by-32 PNG. Use
`uv run pipescaler image process resize --help` for the current options.

## Build a small pipeline

Save this as `example_pipeline.py` in the repository root, then run
`uv run python example_pipeline.py`. It generates two input images, reads them
through a directory source, resizes each image through a pipeline segment, and
writes the results through a directory terminus. Outputs appear under
`local/readme-example/output/`, with the nested input directory preserved.

```python
from pathlib import Path

from PIL import Image

from pipescaler.image.operators.processors.resize_processor import ResizeProcessor
from pipescaler.image.pipelines.segments.image_processor_segment import (
    ImageProcessorSegment,
)
from pipescaler.image.pipelines.sources.image_directory_source import (
    ImageDirectorySource,
)
from pipescaler.image.pipelines.termini.image_directory_terminus import (
    ImageDirectoryTerminus,
)

input_path = Path("local/readme-example/input")
(input_path / "nested").mkdir(parents=True, exist_ok=True)
Image.new("RGB", (16, 16), "coral").save(input_path / "first.png")
Image.new("RGB", (8, 12), "navy").save(input_path / "nested/second.png")

source = ImageDirectorySource(input_path, inclusions={r".*\.png$"})
resize = ImageProcessorSegment(ResizeProcessor(scale=2, resample="nearest"))
terminus = ImageDirectoryTerminus(Path("local/readme-example/output"))
for input_image in source:
    (output_image,) = resize(input_image)
    terminus(output_image)
```

## Find components and contracts

Source docstrings and CLI help own the component inventory, options, and defaults.
Browse [image operators](pipescaler/image/operators/),
[image pipeline components](pipescaler/image/pipelines/),
[image runners](pipescaler/image/runners/),
[video pipeline components](pipescaler/video/pipelines/), and
[video runners](pipescaler/video/runners/). Package `__init__.py` files identify
exports and dependency order. Use `uv run pipescaler image --help` to discover
available image commands.

Developer guidance: [Architecture](docs/ARCHITECTURE.md),
[Code Style](docs/STYLE.md), [Documentation](docs/DOCUMENTATION.md), and
[Contributing](docs/CONTRIBUTING.md). Install development tools with
`uv sync --dev --frozen` and follow the [validation instructions](AGENTS.md#validation).
