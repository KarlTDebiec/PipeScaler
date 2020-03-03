class WaifuProcessor(Processor):
    executable_name = "waifu2x"

    def __init__(self, imagetype: str, scale: str, noise: str,
                 **kwargs: Any) -> None:
        super().__init__(**kwargs)
        self.imagetype = imagetype
        self.scale = scale
        self.noise = noise

    def process_file(self, infile: str, outfile: str) -> None:
        if isfile(outfile):
            return
        print(f"Processing to '{outfile}'")
        command = f"{self.executable} " \
                  f"-t {self.imagetype} " \
                  f"-s {self.scale} " \
                  f"-n {self.noise} " \
                  f"-i {infile} " \
                  f"-o {outfile}"
        print(command)
        Popen(command, shell=True, close_fds=True).wait()

    @classmethod
    def get_processors(cls, **kwargs: Any) -> List[Processor]:
        processors: List[Processor] = []
        imagetypes = kwargs.pop("imagetype")
        scales = kwargs.pop("scale")
        noises = kwargs.pop("noise")
        for imagetype in imagetypes:
            for scale in scales:
                for noise in noises:
                    processors.append(cls(
                        imagetype=imagetype,
                        scale=scale,
                        noise=noise,
                        paramstring=f"waifu-"
                                    f"{imagetype}-"
                                    f"{scale}-"
                                    f"{noise}",
                        **kwargs))
        return processors
