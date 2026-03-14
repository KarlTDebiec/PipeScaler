#  Copyright 2020-2026 Karl T Debiec. All rights reserved. This software may be modified
#  and distributed under the terms of the BSD license. See the LICENSE file for details.
"""Tests for DolphinFileScanner."""

from pathlib import Path

from PIL import Image

from pipescaler.common.file import get_temp_directory_path
from pipescaler.utilities import DolphinFileScanner


def write_png(path: Path):
    """Write a tiny PNG image.

    Arguments:
        path: output file path
    """
    image = Image.new("RGBA", (1, 1), (255, 255, 255, 255))
    image.save(path)


def test_copies_base_texture_without_mip_suffix():
    """Test that the base Dolphin texture is copied normally."""
    with (
        get_temp_directory_path() as input_dir_path,
        get_temp_directory_path() as project_root_path,
    ):
        write_png(input_dir_path / "tex1_256x128_m_e3018a378fd26b5e_14.png")

        file_scanner = DolphinFileScanner(input_dir_path, project_root_path, None, [])
        file_scanner()

        assert (
            project_root_path / "new" / "tex1_256x128_m_e3018a378fd26b5e_14.png"
        ).exists()


def test_ignores_mipmap_textures():
    """Test that Dolphin mipmap textures are ignored."""
    with (
        get_temp_directory_path() as input_dir_path,
        get_temp_directory_path() as project_root_path,
    ):
        write_png(input_dir_path / "tex1_256x128_m_e3018a378fd26b5e_14_mip1.png")

        file_scanner = DolphinFileScanner(input_dir_path, project_root_path, None, [])
        file_scanner()

        assert (
            input_dir_path / "tex1_256x128_m_e3018a378fd26b5e_14_mip1.png"
        ).exists()
        assert not (project_root_path / "new").exists()


def test_base_texture_is_not_treated_as_mipmap_due_to_embedded_m_marker():
    """Test that Dolphin's embedded _m_ segment does not trigger mip ignore."""
    with (
        get_temp_directory_path() as input_dir_path,
        get_temp_directory_path() as project_root_path,
    ):
        write_png(input_dir_path / "tex1_256x128_m_e3018a378fd26b5e_14.png")
        write_png(input_dir_path / "tex1_256x128_m_e3018a378fd26b5e_14_mip2.png")

        file_scanner = DolphinFileScanner(input_dir_path, project_root_path, None, [])
        file_scanner()

        assert (
            project_root_path / "new" / "tex1_256x128_m_e3018a378fd26b5e_14.png"
        ).exists()
        assert (
            input_dir_path / "tex1_256x128_m_e3018a378fd26b5e_14_mip2.png"
        ).exists()
