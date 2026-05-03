# Architecture

PipeScaler processes collections of image and video files through composable pipelines. A pipeline moves `PipeObject` instances from sources through sorters, processors, splitters, mergers, runners, checkpoint wrappers, and termini. Components should stay small and composable so pipelines can be inspected, resumed, and tested one segment at a time.

## Package Layout
* `pipescaler/common/` contains cross-cutting utilities for CLI plumbing, validation, filesystem helpers, logging setup, subprocess execution, exceptions, and test support. Keep domain-specific image or video behavior out of this package.
* `pipescaler/core/` contains generic pipeline primitives that are not tied to a media type, including `PipeObject`, `Segment`, source and terminus bases, sorter bases, checkpoint base behavior, runner support, typing helpers, and shared sorting utilities.
* `pipescaler/pipelines/` contains concrete generic pipeline helpers, including checkpoint management, pre-checkpoint and post-checkpoint segment wrappers, and generic sorters.
* `pipescaler/image/core/` contains image-specific base types and shared image behavior. It should hold abstractions and validation used by multiple image operators, pipelines, or CLIs.
* `pipescaler/image/operators/` contains concrete image transformations. Processors transform one image, splitters separate one image into multiple images, and mergers combine multiple images into one image.
* `pipescaler/image/pipelines/` contains concrete image pipeline sources, sorters, termini, checkpoint behavior, substituters, and segment wrappers that adapt operators or runners into pipeline segments.
* `pipescaler/image/runners/` and `pipescaler/image/utilities/` contain wrappers around external image tools and higher-level utilities respectively.
* `pipescaler/video/core/`, `pipescaler/video/pipelines/`, and `pipescaler/video/runners/` mirror the image layout for video-specific objects, pipeline components, and external tool runners.
* `pipescaler/cli/`, `pipescaler/core/cli/`, and `pipescaler/image/cli/` expose command-line entry points. CLI modules should parse arguments and delegate work to core, operator, pipeline, utility, or runner classes.
* `pipescaler/testing/` contains reusable test helpers for this repository. Keep production code independent from test-only helpers unless a helper is intentionally part of the package's test support surface.
* `test/` mirrors the package layout. Add focused tests beside the behavior being changed.

## Dependency Direction
* Domain-specific packages may depend on `pipescaler.common` and `pipescaler.core`.
* Image and video packages should not depend on each other unless a feature explicitly bridges the domains.
* Concrete operators, runners, sources, sorters, and termini should depend on base abstractions, not on peer concrete implementations unless composition is the feature being implemented.
* CLI modules may depend on concrete implementation modules, but implementation modules should not depend on CLI modules.
* Test helpers may depend on production code; production code should not depend on `test/`.

## Pipeline Model
* `PipeObject` represents the item moving through a pipeline. It tracks a file path, display name, parent objects, and an optional location relative to a source root.
* `Segment` represents one pipeline step. It accepts one or more pipeline objects and returns a tuple of pipeline objects, even when there is only one output.
* Sources create pipeline objects from external input, termini write or collect final output, and sorters route objects into named branches.
* Image and video pipeline classes specialize generic pipeline behavior by binding the object type and media-specific validation or IO.
* Checkpoint managers observe checkpoint names and locations, load current checkpoints when possible, save outputs after segment execution, and remove unrecognized checkpoint files only when explicitly requested.

## Operators And Runners
* Operators should perform deterministic in-memory transformations where practical. Keep file traversal, checkpointing, and pipeline routing outside operator classes.
* Processors, splitters, and mergers should define narrow `__call__` contracts and return new objects or image values without surprising side effects.
* Runners wrap external tools and model execution. Keep subprocess command construction, environment assumptions, and output validation close to the runner class.
* Prefer existing libraries for image processing, video processing, and ML model execution rather than reimplementing specialized algorithms in project code.

## CLIs
* Command-line classes should focus on argument definitions, command dispatch, and translation from CLI values into implementation objects.
* Keep user-facing command output deliberate. Libraries and scripts should use logging for status and diagnostics.
* Reuse validation helpers from `pipescaler.common.validation` for filesystem and argument validation.

## Tests
* Add or update tests under the matching `test/` package path for behavior changes.
* Use repository test fixtures and helpers instead of duplicating temporary file, image, or execution-count setup.
* Mark tests that require serial execution, GUI behavior, external tools, or large resources using the markers configured in `pyproject.toml`.
* Keep checkpoint and pipeline tests explicit about file paths and expected object lineage so resume behavior stays clear.
