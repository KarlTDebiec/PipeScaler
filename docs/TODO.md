TODO:
- [x] Splitters/Mergers: Generic alpha splitter
- [x] Set up black
- [x] Reformat for black and 88 columns
- [x] Standards-compliant filenames
- [x] Sorters: Rename mipmap to scaled
- [x] Stages: Consider Stage base class
- [x] Pipeline: Do not backup until needed
- [x] apng_creator: Support annotation
- [ ] AlphaSplitter/AlphaMerger: Option to keep RGBA for both and stack
- [ ] WaifuPixelmator2XProcessor: Remove
- [ ] SideChannelProcessor: Alternative downstream stages for unmatched
- [ ] common: Review documentation

- [ ] AppleScriptProcessor for Pixelmator
- [ ] ModeChangeProcessor?
- [ ] Splitters/Mergers: normal map
- [ ] Splitters/Mergers: size
- [ ] Processors: Consistent handling of verbosity
- [ ] Processors: Command-line support for all
- [ ] Processors: Do not regenerate objects each call in pipeline
- [ ] Processors: Check if necessary executables exist
- [ ] Processors: Consider if specular maps could be handled better
- [ ] CI: Run black
- [ ] CI: Run mypy
- [ ] CI: Documentation coverage
- [ ] CI: Waifu on Linux (without CUDA?)
- [ ] Windows Support

Notes:
- Don't use a property unless you cannot do the initialization in __init__
- Don't write a setter unless you need to set the value outside of __init__
