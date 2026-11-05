# TemporalFix video checkpoints

`TemporalFixProcessor` wraps the upstream
[vs_temporalfix 2.4.1 model](https://github.com/pifroggi/vs_temporalfix).
It processes constant-rate video files or numbered RGB image sequences without
requiring native video plugins for ordinary PipeScaler image processing.

## Optional runtime

Inspection, graph construction, and frame evaluation run directly in the calling
Python process. Install VapourSynth and backend dependencies in the same Python
3.13 or 3.14 environment as PipeScaler. They load lazily during inspection and
processing, so ordinary image tools do not require them.
The verified Windows CPU combination is Python 3.14.1, VapourSynth R82,
vs_temporalfix 2.4.1, BestSource 23, and PyTorch 2.14.1. CUDA, DirectML, and TensorRT
options are forwarded and probed, but hardware inference for those backends is
unverified. Other platforms may require a separately installed native VapourSynth
runtime; follow the upstream installation instructions.

For example, from the repository on Windows:

```powershell
uv sync --extra temporalfix
```

FFmpeg and ffprobe must be on `PATH`. TensorRT also needs the upstream TensorRT
dependencies and a compatible GPU/runtime. The processor checks the current runtime
and backend before rendering and rejects unsupported TemporalFix versions because
the chunk context depends on its seven-frame model contract.

## Pipeline composition

```python
from pipescaler.pipelines import CheckpointManager
from pipescaler.video.core.pipelines import PipeVideo
from pipescaler.video.core.temporalfix_settings import TemporalFixSettings
from pipescaler.video.pipelines.segments import CheckpointedVideoProcessorSegment
from pipescaler.video.processors import TemporalFixProcessor

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
processor = TemporalFixProcessor(settings)
manager = CheckpointManager("local/video-checkpoints")
segment = CheckpointedVideoProcessorSegment(processor, manager, chunk_frames=48)
(output,) = segment(PipeVideo(path="frames/frame_%06d.png"))
```

Projects choose source paths, scratch locations, cut/exclusion ranges, settings,
audio/subtitles, and delivery encoding.
`processor.process(input_path, output_path)` can also render a selected range
without the checkpoint segment.

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
processing failures or Python interruption. Partial chunks have no completion
manifest and are rerendered. Source changes invalidate newly completed manifests.

Native Python exceptions propagate directly to the caller. There is no processing
timeout or separate process to terminate: `KeyboardInterrupt` takes effect when
native code returns control to Python. A native crash terminates the application;
unresponsive native work requires stopping the application externally. Streamed
encoding has no deadline; FFmpeg concatenation and ffprobe validation use the
subprocess utility's default timeout. On Python exceptions and interruption, the
processor terminates and reaps its FFmpeg encoder and removes temporary output.

The processor writes beside its destination, validates the complete video, and
publishes it by atomic replacement. The checkpoint segment publishes the final
video only after all chunks and the concatenation validate. A crash between video
and manifest publication causes conservative revalidation/rerendering. Previous
valid final videos survive processing failures. Concurrent writers to the same
checkpoint location are unsupported.

Optional real-runtime tests use `PIPESCALER_TEST_TEMPORALFIX=1` to opt into native
dependencies in the current interpreter. From the repository on Windows:

```powershell
$env:PIPESCALER_TEST_TEMPORALFIX = "1"
uv run --extra temporalfix pytest test/video/processors/test_temporalfix_integration.py
```

Their 16-bit fixtures are generated by
[`generate_temporalfix_sample.py`](../test/scripts/generate_temporalfix_sample.py).
Whole/chunked CPU results are compared within two 16-bit code values, including
true clip edges, explicit scenes, exclusions, and short-scene pass-through. Default
unit tests require neither native video plugins nor a GPU.
