class PotraceProcessor(Processor):
    executable_name = "potrace"

    def __init__(self, blacklevel: float, alphamax: float, opttolerance: float,
                 **kwargs: Any) -> None:
        super().__init__(**kwargs)
        self.blacklevel = blacklevel
        self.alphamax = alphamax
        self.opttolerance = opttolerance

    def process_file(self, infile: str, outfile: str) -> None:
        if isfile(outfile):
            return
        print(f"Tracing to '{outfile}'")

        # Convert to bmp; potrace does not accept png
        bmpfile = f"{splitext(infile)[0]}.bmp"
        command = f"convert " \
                  f"{infile} " \
                  f"{bmpfile}"
        print(command)
        Popen(command, shell=True, close_fds=True).wait()

        # trace
        svgfile = f"{splitext(outfile)[0]}.svg"
        command = f"{self.executable} " \
                  f"{bmpfile} " \
                  f"-b svg " \
                  f"-k {self.blacklevel} " \
                  f"-a {self.alphamax} " \
                  f"-O {self.opttolerance} " \
                  f"-o {svgfile}"
        print(command)
        Popen(command, shell=True, close_fds=True).wait()

        # Rasterize svg to png
        pngfile = f"{splitext(outfile)[0]}.png"
        command = f"convert " \
                  f"{svgfile} " \
                  f"{pngfile}"
        print(command)
        Popen(command, shell=True, close_fds=True).wait()

        remove(bmpfile)
        remove(svgfile)

    @classmethod
    def get_processors(cls, **kwargs: Any) -> List[Processor]:
        blacklevels = kwargs.pop("blacklevel")
        if not isinstance(blacklevels, list):
            blacklevels = [blacklevels]
        alphamaxes = kwargs.pop("alphamax")
        if not isinstance(alphamaxes, list):
            alphamaxes = [alphamaxes]
        opttolerances = kwargs.pop("opttolerance")
        if not isinstance(opttolerances, list):
            opttolerances = [opttolerances]

        processors: List[Processor] = []
        for blacklevel in blacklevels:
            for alphamax in alphamaxes:
                for opttolerance in opttolerances:
                    processors.append(cls(
                        blacklevel=blacklevel,
                        alphamax=alphamax,
                        opttolerance=opttolerance,
                        paramstring=f"potrace-"
                                    f"{float(blacklevel):3.2f}-"
                                    f"{alphamax}-"
                                    f"{float(opttolerance):3.1f}",
                        **kwargs))
        return processors
