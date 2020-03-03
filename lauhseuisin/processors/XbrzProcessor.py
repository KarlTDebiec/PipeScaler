class XbrzProcessor(Processor):
    executable_name = "xbrzscale"

    def __init__(self, scale: str, **kwargs: Any) -> None:
        super().__init__(**kwargs)
        self.scale = scale

    def process_file(self, infile: str, outfile: str) -> None:
        if isfile(outfile):
            return
        print(f"Processing to '{outfile}'")
        command = f"{self.executable} " \
                  f"{self.scale} " \
                  f"{infile} " \
                  f"{outfile}"
        print(command)
        Popen(command, shell=True, close_fds=True).wait()

    @classmethod
    def get_processors(cls, **kwargs: Any) -> List[Processor]:
        processors: List[Processor] = []
        scales = kwargs.pop("scale")
        for scale in scales:
            processors.append(cls(
                scale=scale,
                paramstring=f"xbrz-"
                            f"{scale}",
                **kwargs))
        return processors
