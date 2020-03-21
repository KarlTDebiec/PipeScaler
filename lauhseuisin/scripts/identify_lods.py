#!python
#   lauseuisin/scripts/identify_lods.py
#
#   Copyright (C) 2020 Karl T Debiec
#   All rights reserved.
#
#   This software may be modified and distributed under the terms of the
#   BSD license.
################################### MODULES ###################################
from __future__ import annotations

import re
from os import listdir
from os.path import basename, expandvars, splitext, join
from typing import Optional
from os import remove
from IPython import embed
from skimage.metrics import structural_similarity as ssim
from PIL import Image
import numpy as np
import yaml
from itertools import chain

with open("../conf_test.yaml", "r") as f:
    conf = yaml.load(f, Loader=yaml.SafeLoader)

list_sorter_pipes = conf["pipes"]["list_sorter"]["ListSorter"][
    "downstream_pipes_for_filenames"]
known_actor = set(list_sorter_pipes["actors"]["filenames"])
known_interface = set(list_sorter_pipes["interface"]["filenames"])
known_map = set(list_sorter_pipes["maps"]["filenames"])
known_skip = set(list_sorter_pipes["skip"]["filenames"])

known_lodsets = conf["pipes"]["default_lod"]["LODSorter"]["lods"]
known_hires = set(conf["pipes"]["default_lod"]["LODSorter"]["lods"])
known_lores = set(chain.from_iterable(
    [a.values() for a in known_lodsets.values() if a is not None]))

known_nolod = set(yaml.load("""
- tex1_64x128_F221D380B26A96B4_7
- tex1_16x32_5730DDCAD166D246_7
- tex1_32x64_7E20E84DE7FCEBD9_8
- tex1_64x64_8448D01B832E4A16_7
- tex1_32x32_64EB73C64ACC9713_5 
- tex1_64x64_FA76C9D8F781A7A9_7
- tex1_32x32_8B4C48114881A863_7
- tex1_64x64_5B2CCFEE6BC460EF_7 
- tex1_64x64_D0BC1EFC4180DBA4_7
- tex1_64x64_38B2D007E73DC979_7
- tex1_64x64_179F6E553F05E9B1_3
- tex1_64x64_823F9021643C43ED_7
- tex1_64x64_78E9241A7AA834B9_8
- tex1_64x64_4573A97ACDA91299_5
- tex1_128x128_5E289A2DBF405874_5
- tex1_128x64_38B031EFB8E7AC1F_7
- tex1_256x128_41ED86BE223733A8_5
- tex1_128x64_934726D8DFF694DF_5
- tex1_128x128_9B03157D3C9E24C2_5
- tex1_128x128_87773DEA6C5C0874_5
- tex1_128x128_073611CFC594A026_5
- tex1_128x128_EEF278E719905D75_5
- tex1_128x128_A5E43974AF03BC9A_5
- tex1_128x128_F7F8B3919C62EEDB_5
- tex1_128x128_C3065A3F903C037F_2
- tex1_128x128_2F487874BFA22581_5
- tex1_128x128_E188124317180216_5
- tex1_128x128_43CCED9C1399C9F3_7
- tex1_128x128_8F5A90288825949A_5
- tex1_128x128_EEF278E719905D75_5
- tex1_128x128_C8E1DEF51F00CC19_4
- tex1_128x128_1E3BFA6FF9B6C5B4_5
- tex1_128x128_FD018FA8B60C3675_3
- tex1_128x128_FD018FA8B60C3675_3
- tex1_128x128_D7B7471F6C1E8CE7_7
- tex1_128x128_D7B7471F6C1E8CE7_7
- tex1_128x128_64A7A3C355E182CA_7
- tex1_128x128_44F73850AF175006_5
- tex1_256x128_D63D35E4F8884C29_8
- tex1_256x128_81B2806F3CFAAF6C_7
- tex1_256x256_BF257E16A50673BA_7
- tex1_128x128_753B3BF68000DB48_7
- tex1_128x64_934726D8DFF694DF_5
"""))


################################## FUNCTIONS ##################################
def get_name(filename: str) -> str:
    return splitext(basename(filename))[0]


def get_filename(filename: str) -> str:
    return f"{join(input_directory, filename)}.png"


def concatenate_images(full_name: str, half_name: Optional[str] = None,
                       quarter_name: Optional[str] = None):
    full_image = Image.open(get_filename(full_name))
    concatenated_image = Image.new(
        "RGBA", (full_image.size[0] * 3, full_image.size[1]))
    concatenated_image.paste(full_image, (0, 0))
    if half_name is not None:
        half_image = Image.open(get_filename(half_name))
        half_image = half_image.resize(
            full_image.size, resample=Image.LANCZOS)
        concatenated_image.paste(half_image, (full_image.size[0], 0))
    if quarter_name is not None:
        quarter_image = Image.open(get_filename(quarter_name))
        quarter_image = quarter_image.resize(
            full_image.size, resample=Image.LANCZOS)
        concatenated_image.paste(quarter_image, (full_image.size[0] * 2, 0))
    return concatenated_image


def load_half_and_quarter_data():
    half_data = {}
    quarter_data = {}
    for name in [get_name(f) for f in listdir(input_directory)]:
        if name in known_actor:
            continue
        elif name in known_interface:
            continue
        elif name in known_map:
            continue
        elif name in known_skip:
            continue
        elif name in known_nolod:
            continue
        elif name in known_hires:
            continue
        elif name in known_lores:
            continue
        if half_re.match(name):
            half_image = Image.open(get_filename(name))
            half_data[name] = np.array(half_image.convert("RGB"))
        elif quarter_re.match(name):
            quarter_image = Image.open(get_filename(name))
            quarter_data[name] = np.array(quarter_image.convert("RGB"))
    print(len(half_data), len(quarter_data))
    return half_data, quarter_data


def name_sort(filename):
    _, size, code, _ = filename.split("_")
    width, height = size.split("x")
    return int(f"{height}{width}{int(code, 16):022d}")


def print_lodsets(lodsets):
    with open("lodsets.txt", "w") as lodset_outfile, \
            open("lods.txt", "w") as lods_outfile:

        full_names = list(lodsets.keys())
        full_names.sort(key=name_sort)
        for full_name in full_names:
            print(f"{full_name}:")
            lodset_outfile.write(f"{full_name}:\n")

            # Load full image
            full_image = Image.open(get_filename(full_name)).convert("RGB")
            half_size = (full_image.size[0] // 2, full_image.size[1] // 2)
            quarter_size = (full_image.size[0] // 4, full_image.size[1] // 4)

            # Load and score lods
            lods = lodsets[full_name]
            if 0.5 in lods:
                half_name = lods[0.5]
                half_image = Image.open(get_filename(half_name))
                half_datum = np.array(half_image.convert("RGB"))

                half_shrunk_image = full_image.resize(
                    half_size, resample=Image.LANCZOS)
                half_shrunk_datum = np.array(half_shrunk_image)

                half_score = ssim(
                    half_shrunk_datum, half_datum, multichannel=True)

                print(f"  0.5: {lods[0.5]} # {half_score:4.2f}")
                lodset_outfile.write(
                    f"  0.5: {lods[0.5]} # {half_score:4.2f}\n")
                lods_outfile.write(f"- {lods[0.5]}\n")

            if 0.25 in lods:
                quarter_name = lods[0.25]
                quarter_image = Image.open(get_filename(quarter_name))
                quarter_datum = np.array(quarter_image.convert("RGB"))

                quarter_shrunk_image = full_image.resize(
                    quarter_size, resample=Image.LANCZOS)
                quarter_shrunk_datum = np.array(quarter_shrunk_image)

                quarter_score = ssim(
                    quarter_shrunk_datum, quarter_datum, multichannel=True)

                print(f"  0.25: {lods[0.25]} # {quarter_score:4.2f}")
                lodset_outfile.write(
                    f"  0.25: {lods[0.25]} # {quarter_score:4.2f}\n")
                lods_outfile.write(f"- {lods[0.25]}\n")

            # Show debug output
            # if half_score < 0.8 or quarter_score < 0.8:
            #     concatenate_images(
            #         full_name, lods.get(0.5), lods.get(0.25)).show()
            #     input()


#################################### MAIN #####################################
if __name__ == "__main__":
    input_directory = expandvars(
        "$HOME/.local/share/citra-emu/dump/textures/000400000008F900")
    full_size = (128, 256)

    # Prepare sizes and regular expressions
    half_size = (full_size[0] // 2, full_size[1] // 2)
    quarter_size = (full_size[0] // 4, full_size[1] // 4)
    full_re = re.compile(f".*{full_size[0]}x{full_size[1]}.*_1[23]")
    half_re = re.compile(f".*{half_size[0]}x{half_size[1]}.*_1[23]")
    quarter_re = re.compile(f".*{quarter_size[0]}x{quarter_size[1]}.*_1[23]")

    # Load in all data for half and quarter sizes
    half_data, quarter_data = load_half_and_quarter_data()

    # Loop over full-size filenames and identify new lodsets
    new_lodsets = {}
    full_filenames = [f for f in listdir(input_directory) if full_re.match(f)]
    full_filenames.sort(key=name_sort)
    full_names = [get_name(f) for f in full_filenames]
    print(len(full_names))
    for full_name in full_names:

        # Skip known
        if full_name in known_actor:
            continue
        elif full_name in known_interface:
            continue
        elif full_name in known_map:
            continue
        elif full_name in known_skip:
            continue
        elif full_name in known_nolod:
            continue
        elif full_name in known_hires:
            continue
        elif full_name in known_lores:
            continue

        # Load image
        full_image = Image.open(get_filename(full_name))
        full_data = np.array(full_image)

        # Skip text images
        if full_data.shape == (256, 256, 4):
            if full_data[:, :, :3].sum() == 0:
                continue

            # Also prompt to delete datetime text
            y, x, _ = np.where(full_data == 255)
            if (x.size > 0 and y.size > 0 and y.max() == 15 and x.max() < 128):
                full_image.show()
                try:
                    ok = input("Delete time image (y/n)?:")
                except KeyboardInterrupt:
                    print()
                    print("Quitting interactive validation")
                    break
                if ok.lower().startswith("y"):
                    print("removing")
                    remove(f"{join(input_directory, full_name)}.png")
                continue

        # Load image data
        full_image = full_image.convert("RGB")
        full_data = np.array(full_image)

        # print(i)
        # i += 1
        # continue

        # Shrink to half size
        half_shrunk_image = full_image.resize(
            half_size, resample=Image.LANCZOS)
        half_shrunk_datum = np.array(half_shrunk_image)

        # Find best-match half image
        half_best_name = ""
        half_best_score = 0
        for half_name, half_datum in half_data.items():
            score = ssim(
                half_shrunk_datum, half_datum, multichannel=True)
            if score > half_best_score:
                half_best_name = half_name
                half_best_score = score

        # Shrink to quarter size
        quarter_shrunk_image = full_image.resize(
            quarter_size, resample=Image.LANCZOS)
        quarter_shrunk_datum = np.array(quarter_shrunk_image)

        # Find best-match quarter image
        quarter_best_name = ""
        quarter_best_score = 0
        for quarter_name, quarter_datum in quarter_data.items():
            score = ssim(
                quarter_shrunk_datum, quarter_datum, multichannel=True)
            if score > quarter_best_score:
                quarter_best_name = quarter_name
                quarter_best_score = score
        quarter_best_image = Image.fromarray(
            quarter_data[quarter_best_name])

        # Display results
        print(f"{full_name}:")
        print(f"  0.5: {half_best_name} # {half_best_score:4.2f}")
        print(f"  0.25: {quarter_best_name} # {quarter_best_score:4.2f}")
        concatenated_image = concatenate_images(
            full_name, half_best_name, quarter_best_name)

        if half_best_score > 0.99 and quarter_best_score > 0.99:
            continue
        elif half_best_score > 0.94 and quarter_best_score > 0.94:
            new_lodsets[full_name] = {
                0.5: half_best_name,
                0.25: quarter_best_name}
            concatenated_image.show()
        else:
            continue

    # Print sets
    known_lodsets.update(new_lodsets)
    print_lodsets(known_lodsets)
    # print_lodsets(new_lodsets)
