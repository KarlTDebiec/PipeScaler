# TemporalFix video checkpoints

`TemporalFixRunner` wraps the upstream
[vs_temporalfix 2.4.1 model](https://github.com/pifroggi/vs_temporalfix).
It processes constant-rate video files or numbered RGB image sequences without
requiring native video plugins for ordinary PipeScaler image processing.

## Worker runtime

The worker interpreter supports Python 3.13 and 3.14. It defaults to the calling
interpreter; a separate environment can keep VapourSynth and backend dependencies
outside the main application environment.
The verified Windows CPU combination is Python 3.14.1, VapourSynth R82,
vs_temporalfix 2.4.1, BestSource 23, and PyTorch 2.14.1. CUDA, DirectML, and TensorRT
options are forwarded and probed, but hardware inference for those backends is
unverified. Other platforms may require a separately installed native VapourSynth
runtime; follow the upstream installation instructions.

Apple Silicon workers can select `backend="mps"`. PipeScaler runs the upstream
2.4.1 architecture and checkpoints on MPS in FP32, including strength
interpolation, upstream spatial tiling, reflected edges, and exclusions. GPU
index zero is the only supported MPS device. Weight interpolation and frame IO
use CPU FP32; model inference uses MPS tensors. Missing MPS hardware and
`PYTORCH_ENABLE_MPS_FALLBACK=1` are rejected before rendering. The loaded model
and its frame cache belong to each graph; inference is serialized within that
graph. FP32 MPS results may differ slightly from CPU or CUDA results.

The worker retains virtual-environment interpreter paths, including symlinked
Python executables on macOS. Resolving such a symlink to its base Python would
discard the selected environment and its installed native packages.

For example, from the repository on Windows:

```powershell
uv venv --python 3.14 local/temporalfix-runtime
uv pip install --python local/temporalfix-runtime/Scripts/python.exe `
    vs_temporalfix==2.4.1 vapoursynth-bestsource==23 torch numpy opencv-python
```

FFmpeg and ffprobe must be on `PATH`. TensorRT also needs the upstream TensorRT
dependencies and a compatible GPU/runtime. The adapter checks the selected worker
and backend before rendering and rejects unsupported TemporalFix versions because
the chunk context depends on its seven-frame model contract.

## Pipeline composition

```python
from pathlib import Path

from pipescaler.pipelines import CheckpointManager
from pipescaler.video.core.pipelines import PipeVideo
from pipescaler.video.core.temporalfix_settings import TemporalFixSettings
from pipescaler.video.pipelines.segments import CheckpointedVideoRunnerSegment
from pipescaler.video.runners import TemporalFixRunner

settings = TemporalFixSettings(
    matrix="709",
    color_range="full",
    frame_rate="24000/1001",
    strength=2.0,
    backend="cpu",
    frame_range=(0, 240),
    scene_boundaries=(120,),
    exclude_ranges=((80, 96),),
)
runner = TemporalFixRunner(
    settings,
    worker_python_path=Path("local/temporalfix-runtime/Scripts/python.exe"),
    timeout=3600,
)
manager = CheckpointManager("local/video-checkpoints")
segment = CheckpointedVideoRunnerSegment(runner, manager, chunk_frames=48)
(output,) = segment(PipeVideo(path="frames/frame_%06d.png"))
```

Projects choose source paths, scratch locations, cut/exclusion ranges, settings,
audio/subtitles, and delivery encoding. `runner.run(input_path, output_path)` can
also render a selected range without the checkpoint segment.

## Timing, color, and context

- All frame intervals are zero-based and half-open. A scene boundary identifies
  the first frame of the next scene. Exclusions are translated to the upstream
  inclusive syntax within each processing window.
- Numbered RGB sequences require an explicit positive rational frame rate and
  `color_range="full"`. 8-bit and 16-bit three-channel images retain frame order.
  Video files use BestSource's native rational rate unless explicitly overridden.
  Variable-rate timelines are unsupported; an explicit rate defines a CFR timeline.
- Supply the input YUV matrix and sample range explicitly for video. RGB sources
  skip matrix conversion. The adapter does not tone-map or change transfer curves.
- Each chunk receives three context frames on either side, limited by true clip
  and supplied scene boundaries. Context outputs are trimmed. The adapter performs
  no automatic scene detection. Scenes shorter than four frames pass through;
  complete inputs shorter than four frames or with odd dimensions are rejected.
- Upstream filtering uses floating-point RGB. The file boundary explicitly rounds
  once to 16-bit planar RGB and encodes losslessly with FFV1 in MKV. Audio and
  subtitles are omitted. Concatenation resets packet timestamps to the exact
  rational frame rate; MKV timestamps retain the container's millisecond precision.
  Validation decodes all frames and checks dimensions, count, format, and timing.

## Checkpoints and failures

Checkpoint identity includes ordered source paths/content hashes, effective
settings and ranges, model fingerprints, dependency versions, adapter code, and
FFmpeg/ffprobe versions. Loaded decoder/filter plugin versions and binary hashes
also participate. Hashing a large source adds sequential I/O on each run.
Completed chunks have independent content-digest manifests and survive later
worker failure, cancellation, or timeout. Partial chunks have no completion
manifest and are rerendered. Source changes invalidate newly completed manifests.

The worker writes beside its destination, validates the complete video, and
publishes it by atomic replacement. The checkpoint segment publishes the final
video only after all chunks and the concatenation validate. A crash between video
and manifest publication causes conservative revalidation/rerendering. Previous
valid final videos survive processing failures. Concurrent writers to the same
checkpoint location are unsupported.

Optional real-runtime tests use `PIPESCALER_TEMPORALFIX_PYTHON` to select the worker.
Their 16-bit fixtures are generated by
[`generate_temporalfix_sample.py`](../test/scripts/generate_temporalfix_sample.py).
Whole/chunked CPU results are compared within two 16-bit code values, including
true clip edges, explicit scenes, exclusions, and short-scene pass-through. Default
unit tests require neither native video plugins nor a GPU.
The same worker checks run on MPS when available. Additional optional checks
compare real MPS FP32 against CPU FP32 within four 16-bit code values and inspect
actual input/weight devices, integer/interpolated strengths, and spatial tiling.
MPS precision and Metal kernel environment settings participate in runtime
identity, alongside the MPS adapter's source hash.
