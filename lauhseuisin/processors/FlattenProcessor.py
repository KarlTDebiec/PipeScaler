class FlattenProcessor(Processor):
    def process_file(self, infile: str, outfile: str) -> None:
        if isfile(outfile):
            return
        print(f"Flattening to '{outfile}'")
        input_data = np.array(Image.open(infile))
        output_data = np.ones_like(input_data) * 255
        output_data[:, :, 0] = 255 - input_data[:, :, 3]
        output_data[:, :, 1] = 255 - input_data[:, :, 3]
        output_data[:, :, 2] = 255 - input_data[:, :, 3]
        output_data[:, :, :3] += input_data[:, :, :3]
        Image.fromarray(output_data).convert("RGB").save(outfile)

    @classmethod
    def get_processors(cls, **kwargs: Any) -> List[Processor]:
        return [cls(paramstring=f"flatten")]
