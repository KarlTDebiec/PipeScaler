#  Copyright 2020-2026 Karl T Debiec. All rights reserved. This software may be modified
#  and distributed under the terms of the BSD license. See the LICENSE file for details.
"""Tests for CitraFileScanner."""

from pathlib import Path

from PIL import Image

from pipescaler.common.file import get_temp_directory_path
from pipescaler.utilities import CitraFileScanner


def write_png(path: Path):
    """Write a tiny PNG image.

    Arguments:
        path: output file path
    """
    image = Image.new("RGBA", (1, 1), (255, 255, 255, 255))
    image.save(path)


def test_removes_legacy_file_when_mip_variant_exists():
    """Test that legacy non-mip file is removed when _mip variant exists."""
    with (
        get_temp_directory_path() as input_dir_path,
        get_temp_directory_path() as project_root_path,
    ):
        write_png(input_dir_path / "tex1_16x16_HASH_12.png")
        write_png(input_dir_path / "tex1_16x16_HASH_12_mip0.png")

        file_scanner = CitraFileScanner(input_dir_path, project_root_path, None, [])
        file_scanner()

        assert not (input_dir_path / "tex1_16x16_HASH_12.png").exists()
        assert (project_root_path / "new" / "tex1_16x16_HASH_12.png").exists()
        assert not (project_root_path / "new" / "tex1_16x16_HASH_12_mip0.png").exists()


def test_ignores_nonzero_mip_files():
    """Test that mip levels greater than 0 are ignored."""
    with (
        get_temp_directory_path() as input_dir_path,
        get_temp_directory_path() as project_root_path,
    ):
        write_png(input_dir_path / "tex1_16x16_HASH_12_mip1.png")

        file_scanner = CitraFileScanner(input_dir_path, project_root_path, None, [])
        file_scanner()

        assert (input_dir_path / "tex1_16x16_HASH_12_mip1.png").exists()
        assert not (project_root_path / "new").exists()


def test_treats_mip0_as_known_when_base_name_reviewed():
    """Test that mip0 file is treated as known if base name is reviewed."""
    with (
        get_temp_directory_path() as input_dir_path,
        get_temp_directory_path() as project_root_path,
    ):
        reviewed_dir_path = project_root_path / "reviewed"
        reviewed_dir_path.mkdir(parents=True)

        write_png(input_dir_path / "tex1_16x16_HASH_12_mip0.png")
        write_png(reviewed_dir_path / "tex1_16x16_HASH_12.png")

        file_scanner = CitraFileScanner(
            input_dir_path, project_root_path, reviewed_dir_path, []
        )
        file_scanner()

        assert not (project_root_path / "new").exists()
        assert (reviewed_dir_path / "tex1_16x16_HASH_12.png").exists()


def test_treats_non_mip_file_normally_without_analog():
    """Test that a non-mip file is handled normally when no mip analog exists."""
    with (
        get_temp_directory_path() as input_dir_path,
        get_temp_directory_path() as project_root_path,
    ):
        write_png(input_dir_path / "tex1_16x16_HASH_12.png")

        file_scanner = CitraFileScanner(input_dir_path, project_root_path, None, [])
        file_scanner()

        assert (project_root_path / "new" / "tex1_16x16_HASH_12.png").exists()


def test_remove_operation_removes_mip_variants():
    """Test that remove operation also removes sibling mip files."""
    with (
        get_temp_directory_path() as input_dir_path,
        get_temp_directory_path() as project_root_path,
    ):
        write_png(input_dir_path / "tex1_16x16_HASH_12.png")
        write_png(input_dir_path / "tex1_16x16_HASH_12_mip0.png")
        write_png(input_dir_path / "tex1_16x16_HASH_12_mip1.png")

        file_scanner = CitraFileScanner(
            input_dir_path,
            project_root_path,
            None,
            rules=[("^tex1_16x16_HASH_12$", "remove")],
        )
        file_scanner()

        assert not (input_dir_path / "tex1_16x16_HASH_12.png").exists()
        assert not (input_dir_path / "tex1_16x16_HASH_12_mip0.png").exists()
        assert not (input_dir_path / "tex1_16x16_HASH_12_mip1.png").exists()


def test_remove_directory_entry_removes_mip_variants():
    """Test that remove-dir entries remove base and mip variants from input."""
    with (
        get_temp_directory_path() as input_dir_path,
        get_temp_directory_path() as project_root_path,
    ):
        remove_dir_path = project_root_path / "remove"
        remove_dir_path.mkdir(parents=True)

        write_png(input_dir_path / "tex1_16x16_HASH_12.png")
        write_png(input_dir_path / "tex1_16x16_HASH_12_mip0.png")
        write_png(input_dir_path / "tex1_16x16_HASH_12_mip1.png")
        write_png(remove_dir_path / "tex1_16x16_HASH_12.png")

        file_scanner = CitraFileScanner(input_dir_path, project_root_path, None, [])
        file_scanner()

        assert not (input_dir_path / "tex1_16x16_HASH_12.png").exists()
        assert not (input_dir_path / "tex1_16x16_HASH_12_mip0.png").exists()
        assert not (input_dir_path / "tex1_16x16_HASH_12_mip1.png").exists()


def test_nonzero_mip_removes_matching_reviewed_file():
    """Test that nonzero mip file removes matching reviewed base file."""
    with (
        get_temp_directory_path() as input_dir_path,
        get_temp_directory_path() as project_root_path,
    ):
        reviewed_dir_path = project_root_path / "reviewed"
        reviewed_dir_path.mkdir(parents=True)

        write_png(input_dir_path / "tex1_16x16_HASH_12_mip1.png")
        write_png(reviewed_dir_path / "tex1_16x16_HASH_12.png")

        file_scanner = CitraFileScanner(
            input_dir_path, project_root_path, reviewed_dir_path, []
        )
        file_scanner()

        assert not (reviewed_dir_path / "tex1_16x16_HASH_12.png").exists()


def test_nonzero_mip_does_not_remove_reviewed_when_mip0_exists():
    """Test nonzero mip does not remove reviewed file when mip0 is present."""
    with (
        get_temp_directory_path() as input_dir_path,
        get_temp_directory_path() as project_root_path,
    ):
        reviewed_dir_path = project_root_path / "reviewed"
        reviewed_dir_path.mkdir(parents=True)

        write_png(input_dir_path / "tex1_16x16_HASH_12_mip0.png")
        write_png(input_dir_path / "tex1_16x16_HASH_12_mip1.png")
        write_png(reviewed_dir_path / "tex1_16x16_HASH_12.png")

        file_scanner = CitraFileScanner(
            input_dir_path, project_root_path, reviewed_dir_path, []
        )
        file_scanner()

        assert (reviewed_dir_path / "tex1_16x16_HASH_12.png").exists()


def test_nonzero_mip_removes_matching_reviewed_file_in_all_review_dirs():
    """Test that nonzero mip removes all matching reviewed files across dirs."""
    with (
        get_temp_directory_path() as input_dir_path,
        get_temp_directory_path() as project_root_path,
    ):
        reviewed_dir_path_1 = project_root_path / "reviewed_a"
        reviewed_dir_path_2 = project_root_path / "reviewed_b"
        reviewed_dir_path_1.mkdir(parents=True)
        reviewed_dir_path_2.mkdir(parents=True)

        write_png(input_dir_path / "tex1_16x16_HASH_12_mip2.png")
        write_png(reviewed_dir_path_1 / "tex1_16x16_HASH_12.png")
        write_png(reviewed_dir_path_2 / "tex1_16x16_HASH_12.png")

        file_scanner = CitraFileScanner(
            input_dir_path,
            project_root_path,
            [reviewed_dir_path_1, reviewed_dir_path_2],
            [],
        )
        file_scanner()

        assert not (reviewed_dir_path_1 / "tex1_16x16_HASH_12.png").exists()
        assert not (reviewed_dir_path_2 / "tex1_16x16_HASH_12.png").exists()


def test_nonzero_mip_removes_matching_reviewed_file_with_remove_prefix():
    """Test nonzero mip invalidates reviewed state with configured remove_prefix."""
    with (
        get_temp_directory_path() as input_dir_path,
        get_temp_directory_path() as project_root_path,
    ):
        reviewed_dir_path = project_root_path / "reviewed"
        reviewed_dir_path.mkdir(parents=True)

        write_png(input_dir_path / "pre_tex1_16x16_HASH_12_mip1.png")
        write_png(reviewed_dir_path / "tex1_16x16_HASH_12.png")

        file_scanner = CitraFileScanner(
            input_dir_path,
            project_root_path,
            reviewed_dir_path,
            [],
            remove_prefix="pre_",
        )

        file_scanner.reviewed_paths_by_base_name = (
            file_scanner.get_reviewed_paths_by_base_name()
        )
        file_scanner.remove_reviewed_paths_for_mip(
            input_dir_path / "pre_tex1_16x16_HASH_12_mip1.png"
        )

        assert not (reviewed_dir_path / "tex1_16x16_HASH_12.png").exists()
        assert "tex1_16x16_HASH_12" not in file_scanner.reviewed_names


def test_cleanup_updates_mip_coexistence_snapshot_before_operations():
    """Test mip coexistence checks use post-cleanup input directory state."""
    with (
        get_temp_directory_path() as input_dir_path,
        get_temp_directory_path() as project_root_path,
    ):
        remove_dir_path = project_root_path / "remove"
        remove_dir_path.mkdir(parents=True)

        write_png(input_dir_path / "tex1_16x16_HASH_12.png")
        write_png(input_dir_path / "tex1_16x16_HASH_12_mip1.png")
        write_png(remove_dir_path / "tex1_16x16_HASH_12_mip1.png")

        file_scanner = CitraFileScanner(input_dir_path, project_root_path, None, [])
        file_scanner()

        assert (project_root_path / "new" / "tex1_16x16_HASH_12.png").exists()
        assert (input_dir_path / "tex1_16x16_HASH_12.png").exists()
