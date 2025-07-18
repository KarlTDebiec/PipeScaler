#  Copyright 2020-2025 Karl T Debiec. All rights reserved. This software may be modified
#  and distributed under the terms of the BSD license. See the LICENSE file for details.
"""Runs Topaz Video AI."""

from __future__ import annotations

from logging import debug
from pathlib import Path

from pipescaler.common.general import run_command
from pipescaler.common.validation import validate_input_directory
from pipescaler.core import Runner


class TopazVideoAiRunner(Runner):
    """Runs Topaz Video AI."""

    proteus_4_3 = (
        '"-hide_banner" "-nostdin" "-y" "-nostats" '
        '"-framerate" "30" "-start_number" "1" '
        '"-i" "{input_path}" '
        '"-sws_flags" "spline+accurate_rnd+full_chroma_int" '
        '"-color_trc" "2" "-colorspace" "2" "-color_primaries" "2" '
        '"-filter_complex" "veai_up=model=prob-3:scale=0:w=2880:h=2160:preblur=0:'
        "noise=0:details=0:halo=0:blur=0:compression=0:estimate=20:device=0:"
        'vram=0.9:instances=1,scale=w=2880:h=2160:flags=lanczos:threads=0" '
        '"-c:v" "png" "-pix_fmt" "rgb24" '
        '"-start_number" "1" '
        '"{output_path}"'
    )
    proteus_16_9 = (
        '"-hide_banner" "-nostdin" "-y" "-nostats" '
        '"-framerate" "30" "-start_number" "1" '
        '"-i" "{input_path}" '
        '"-sws_flags" "spline+accurate_rnd+full_chroma_int" '
        '"-color_trc" "2" "-colorspace" "2" "-color_primaries" "2" '
        '"-filter_complex" "veai_up=model=prob-3:scale=0:w=3840:h=2160:preblur=0:'
        "noise=0:details=0:halo=0:blur=0:compression=0:estimate=20:device=0:"
        'vram=0.9:instances=1,scale=w=3840:h=2160:flags=lanczos:threads=0" '
        '"-c:v" "png" "-pix_fmt" "rgb24" '
        '"-start_number" "1" '
        '"{output_path}"'
    )
    chronos_60 = (
        '"-hide_banner" "-nostdin" "-y" "-nostats" '
        '"-framerate" "30" "-start_number" "1" '
        '"-i" "{input_path}" '
        '"-sws_flags" "spline+accurate_rnd+full_chroma_int" '
        '"-color_trc" "2" "-colorspace" "2" "-color_primaries" "2" '
        '"-filter_complex" "veai_fi=model=chf-3:slowmo=1:fps=60:device=0:vram=0.9:'
        'instances=1" '
        '"-c:v" "h264_nvenc" "-profile:v" "high" "-preset" "medium" '
        '"-pix_fmt" "yuv420p" "-b:v" "0" '
        '"-movflags" '
        '"frag_keyframe+empty_moov+delay_moov+use_metadata_tags+write_colr "'
        ' "-map_metadata:s:v" "0:s:v" "-an" '
        ' "{output_path}"'
    )
    chronos_60_prores = (
        '"-hide_banner" "-nostdin" "-y" "-nostats" '
        '"-framerate" "30" "-start_number" "1" '
        '"-i" "{input_path}" '
        '"-sws_flags" "spline+accurate_rnd+full_chroma_int" '
        '"-color_trc" "2" "-colorspace" "2" "-color_primaries" "2" '
        '"-filter_complex" "veai_fi=model=chf-3:slowmo=1:fps=60:device=0:vram=0.9:'
        'instances=1" '
        '"-c:v" "prores_ks" "-profile:v" "1" "-vendor" "apl0" "-bits_per_mb" "8000" '
        '"-pix_fmt" "yuv422p10le" "-map_metadata" "0" '
        '"-movflags" '
        '"frag_keyframe+empty_moov+delay_moov+use_metadata_tags+write_colr " '
        '"-map_metadata:s:v" "0:s:v" "-an" '
        ' "{output_path}"'
    )

    def __init__(
        self,
        arguments: str,
        working_directory: str = r"C:\Program Files\Topaz Labs LLC\Topaz Video AI",
        **kwargs,
    ) -> None:
        """Initialize.

        Arguments:
            arguments: Command-line arguments to pass to Topaz Video AI
            working_directory: Directory in which Topaz Video AI is installed
            kwargs: Additional keyword arguments
        """
        super().__init__(**kwargs)

        self.arguments = arguments
        self.working_directory = validate_input_directory(working_directory)

    def __repr__(self) -> str:
        """Representation."""
        return f"{self.__class__.__name__}(arguments={self.arguments!r})"

    @property
    def command_template(self) -> str:
        """String template with which to generate command."""
        return f'cd "{self.working_directory}" & ffmpeg {self.arguments}'

    @property
    def executable_path(self) -> Path:
        """Path to executable."""
        # TODO: Check environment variables?
        # TODO: Actually validate executable?
        return Path(self.executable())

    def run(self, input_path: Path | str, output_path: Path | str) -> None:
        """Run executable on input file, yielding output file.

        Arguments:
            input_path: Input file path
            output_path: Output file path
        """
        command = self.command_template.format(
            input_path=input_path, output_path=output_path
        )
        debug(f"{self}: {command}")
        # TODO: Improve this
        run_command(command)

    @classmethod
    def executable(cls) -> str:
        """Name of executable."""
        return "ffmpeg"

    @classmethod
    def help_markdown(cls) -> str:
        """Short description of this tool in markdown, with links."""
        return (
            "Upscales and/or denoises video using [Topaz Video AI]"
            "(https://www.topazlabs.com/topaz-video-ai)."
        )
