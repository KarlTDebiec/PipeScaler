## TODO:

- [ ] CopyFileProcessor: Option to force overwrite, or to check timestamp and overwrite
  if newer
- [ ] BethesdaArchiveSource and folder support
- [ ] Filetype sorter
- [ ] AlphaSplitter/AlphaMerger: Option to keep RGBA for both and stack
- [ ] WaifuPixelmator2XProcessor: Remove
- [ ] SideChannelProcessor: Alternative downstream stages for unmatched
- [ ] common: Review documentation
- [ ] AppleScriptProcessor for Pixelmator
- [ ] ModeChangeProcessor?
- [ ] Splitters/Mergers: split into components of defined size and pipe separately
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

## Notes:

- Don't use a property unless you cannot do the initialization in __init__
- Don't write a setter unless you need to set the value outside of __init__
