#  Copyright 2026 Karl T Debiec. All rights reserved. This software may be modified
#  and distributed under the terms of the BSD license. See the LICENSE file for details.
"""Write images directly into resumable, atomic checkpoints."""

from __future__ import annotations

from logging import getLogger

from PIL import Image

from pipescaler.common.file import get_temp_file_path
from pipescaler.core.pipelines import CheckpointManagerBase
from pipescaler.image.core.pipelines import ImageSegment, PipeImage
from pipescaler.image.core.typing import ImageWriterLike

__all__ = ["CheckpointedImageWriterSegment"]

logger = getLogger(__name__)


class CheckpointedImageWriterSegment(ImageSegment):
    """Save an image with an in-process writer, preserving its encoded file.

    Existing checkpoints use the manager's freshness policy. Writes are validated
    by loading their base image before publication. Input identity and lineage are
    retained, and a failed write leaves any prior checkpoint intact.
    """

    def __init__(
        self, writer: ImageWriterLike, cp_manager: CheckpointManagerBase, cpt: str
    ):
        """Store the writer and checkpoint configuration.

        Arguments:
            writer: callable accepting Pillow pixels and an output path
            cp_manager: manager owning checkpoint freshness and observation
            cpt: checkpoint filename, including its extension
        """
        self.writer = writer
        """In-process image writer."""
        self.cp_manager = cp_manager
        """Manager owning this checkpoint."""
        self.cpts = (cpt,)
        """Checkpoint names, available to enclosing checkpoint decorators."""

    def __call__(self, *input_objs: PipeImage) -> tuple[PipeImage, ...]:
        """Return the existing checkpoint or write the input pixels directly.

        Arguments:
            *input_objs: exactly one source image
        Returns:
            file-backed output image with the input as its parent
        Raises:
            ValueError: if the number of inputs is not one
            OSError: if writing or validating the checkpoint fails
        """
        if len(input_objs) != 1:
            raise ValueError("CheckpointedImageWriterSegment requires 1 input.")
        input_obj = input_objs[0]
        cpt = self.cpts[0]
        cpt_path = self.cp_manager.dir_path / input_obj.location_name / cpt
        if cpt_path.exists() and self.cp_manager.checkpoints_current(
            input_objs, [cpt_path]
        ):
            logger.info(
                f"{self}: '{input_obj.location_name}' checkpoint '{cpt}' loaded"
            )
        else:
            cpt_path.parent.mkdir(parents=True, exist_ok=True)
            with get_temp_file_path(
                cpt_path.suffix, parent_dir_path=cpt_path.parent
            ) as temp_path:
                self.writer(input_obj.image, temp_path)
                with Image.open(temp_path) as image:
                    image.load()
                temp_path.replace(cpt_path)
            logger.info(f"{self}: '{input_obj.location_name}' checkpoint '{cpt}' saved")
        self.cp_manager.observe(input_obj.location_name, cpt)
        return (PipeImage(path=cpt_path, parents=input_obj),)

    def __repr__(self) -> str:
        """Describe the writer and checkpoint configuration.

        Returns:
            reconstructible segment configuration
        """
        return (
            f"{self.__class__.__name__}(writer={self.writer!r}, "
            f"cp_manager={self.cp_manager!r}, cpt={self.cpts[0]!r})"
        )
