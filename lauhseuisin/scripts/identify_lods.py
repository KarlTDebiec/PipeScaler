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
from copy import deepcopy
from itertools import chain
from os import listdir, remove, stat
from os.path import basename, expandvars, join, splitext, isfile
from readline import insert_text, redisplay, set_pre_input_hook
from typing import Optional, Dict

import numpy as np
import yaml
from datetime import datetime
from IPython import embed
from PIL import Image
from skimage.metrics import structural_similarity as ssim

with open("../actors.yaml", "r") as f:
    known_actor = yaml.load(f, Loader=yaml.SafeLoader)
with open("../interface.yaml", "r") as f:
    known_interface = yaml.load(f, Loader=yaml.SafeLoader)
with open("../maps.yaml", "r") as f:
    known_map = yaml.load(f, Loader=yaml.SafeLoader)
with open("../skip.yaml", "r") as f:
    known_skip = yaml.load(f, Loader=yaml.SafeLoader)
with open("../lodsets.yaml", "r") as f:
    known_lodsets = yaml.load(f, Loader=yaml.SafeLoader)
known_hires = known_lodsets.keys()
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
""", Loader=yaml.SafeLoader))


################################## FUNCTIONS ##################################
def get_name(filename: str) -> str:
    return splitext(basename(filename))[0]


def get_lores_filename(filename: str) -> str:
    return f"{join(lores_directory, filename)}.png"


def get_hires_filename(filename: str) -> str:
    return f"{join(hires_directory, filename)}.png"


def concatenate_images(lodset: Dict[float, str]) -> Image.Image:
    # Load and paste full image
    full_image = Image.open(get_lores_filename(lodset[1.0]))
    concatenated_image = Image.new(
        "RGBA", (full_image.size[0] * 4, full_image.size[1] * 2))
    concatenated_image.paste(full_image, (0, 0))
    if isfile(get_hires_filename(lodset[1.0])):
        full_hires_image = Image.open(get_hires_filename(lodset[1.0]))
        full_hires_image = full_hires_image.resize(
            full_image.size, resample=Image.LANCZOS)
        concatenated_image.paste(
            full_hires_image, (0, full_image.size[1]))

    # Load and paste LODs
    for i, size in enumerate([0.5, 0.25, 0.125], 1):
        if size in lodset:
            lod_image = Image.open(get_lores_filename(lodset[size]))
            lod_image = lod_image.resize(
                full_image.size, resample=Image.LANCZOS)
            concatenated_image.paste(lod_image, (full_image.size[0] * i, 0))
            if isfile(get_hires_filename(lodset[size])):
                lod_hires_image = Image.open(get_hires_filename(lodset[size]))
                lod_hires_image = lod_hires_image.resize(
                    full_image.size, resample=Image.LANCZOS)
                concatenated_image.paste(
                    lod_hires_image,
                    (full_image.size[0] * i, full_image.size[1]))

    return concatenated_image


def input_prefill(prompt: str, prefill: str) -> str:
    def pre_input_hook() -> None:
        insert_text(prefill)
        redisplay()

    set_pre_input_hook(pre_input_hook)
    result = input(prompt)
    set_pre_input_hook()

    return result


def load_data():
    data = {1.0: {}, 0.5: {}, 0.25: {}, 0.125: {}}
    for name in [get_name(f) for f in listdir(lores_directory)]:
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
        for size in [1.0, 0.5, 0.25, 0.125]:
            if regexes[size].match(name):
                image = Image.open(get_lores_filename(name))
                datum = np.array(image)
                if datum.shape == (256, 256, 4):
                    if datum[:, :, :3].sum() == 0:
                        continue
                    y, x, _ = np.where(datum == 255)
                    if (x.size > 0 and y.size > 0
                            and y.max() == 15 and x.max() < 128):
                        continue
                data[size][name] = np.array(image.convert("RGB"))

    print(len(data[1.0]), len(data[0.5]), len(data[0.25]), len(data[0.125]))
    return data


def name_sort(filename):
    _, size, code, _ = filename.split("_")
    width, height = size.split("x")
    return int(f"{height}{width}{int(code, 16):022d}")


def print_lodsets(lodsets):
    with open("../lodsets.yaml", "w") as lodset_outfile, \
            open("../lods.yaml", "w") as lods_outfile:

        full_names = list(lodsets.keys())
        full_names.sort(key=name_sort)
        for full_name in full_names:
            print(f"{full_name}:")
            lodset_outfile.write(f"{full_name}:\n")

            # Load full image
            full_image = Image.open(get_lores_filename(full_name)).convert(
                "RGB")
            half_size = (full_image.size[0] // 2, full_image.size[1] // 2)
            quarter_size = (full_image.size[0] // 4, full_image.size[1] // 4)
            eighth_size = (full_image.size[0] // 8, full_image.size[1] // 8)

            # Load and score lods
            lods = lodsets[full_name]
            if 0.5 in lods:
                half_name = lods[0.5]
                half_image = Image.open(get_lores_filename(half_name))
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
                quarter_image = Image.open(get_lores_filename(quarter_name))
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
            if 0.125 in lods:
                eighth_name = lods[0.125]
                eighth_image = Image.open(get_lores_filename(eighth_name))
                eighth_datum = np.array(eighth_image.convert("RGB"))

                eighth_shrunk_image = full_image.resize(
                    eighth_size, resample=Image.LANCZOS)
                eighth_shrunk_datum = np.array(eighth_shrunk_image)

                eighth_score = ssim(
                    eighth_shrunk_datum, eighth_datum, multichannel=True)

                print(f"  0.25: {lods[0.125]} # {eighth_score:4.2f}")
                lodset_outfile.write(
                    f"  0.25: {lods[0.125]} # {eighth_score:4.2f}\n")
                lods_outfile.write(f"- {lods[0.125]}\n")


def write_lods(lodsets):
    lods = set()

    full_names = list(lodsets.keys())
    full_names.sort(key=name_sort)
    for full_name in full_names:
        for size, name in lodsets[full_name].items():
            lods.add(name)

    lods = list(lods)
    lods.sort(key=name_sort)
    with open("../lods.yaml", "w") as lods_outfile:
        for name in lods:
            lods_outfile.write(f"- {name}\n")


#################################### MAIN #####################################
if __name__ == "__main__":

    # Configuration
    lores_directory = expandvars(
        "$HOME/.local/share/citra-emu/dump/textures/000400000008F900/")
    hires_directory = expandvars(
        "$HOME/Documents/Zelda/4x_kdebiec/")
    lodset_directory = expandvars("$HOME/Documents/Zelda/4x_lodsets")
    threshold = 0.65

    # Clean up existing data
    for filename in listdir(lodset_directory):
        print(f"Removing {filename}")
        remove(f"{lodset_directory}/{filename}")
    write_lods(known_lodsets)

    for full_size in [(64,64)]:
        # Prepare sizes and regular expressions
        sizes = {1.0: full_size}
        regexes = {1.0: re.compile(
            f".*_{sizes[1.0][0]}x{sizes[1.0][1]}_.*_1[23]")}
        for size in [0.5, 0.25, 0.125]:
            sizes[size] = (sizes[1.0][0] // int(1 / size),
                           sizes[1.0][1] // int(1 / size))
            regexes[size] = re.compile(
                f".*_{sizes[size][0]}x{sizes[size][1]}_.*_1[23]")

        # Load in all data for half and quarter sizes
        data = load_data()

        # Validate timestamps
        for full_name, full_datum in data[1.0].items():
            if full_name not in known_lodsets:
                continue
            questionable = False
            full_creation_time = datetime.fromtimestamp(
                stat(get_lores_filename(full_name)).st_birthtime)
            lods = deepcopy(known_lodsets.get(full_name, {}))
            lods[1.0] = full_name
            print(f"{full_name}: {full_creation_time}")
            for size in [0.5, 0.25, 0.125]:
                if size not in lods:
                    continue
                name = lods[size]
                creation_time = datetime.fromtimestamp(
                    stat(get_lores_filename(name)).st_birthtime)
                delta_time = abs(
                    (full_creation_time - creation_time).total_seconds())
                if delta_time > 1:
                    questionable = True
                print(f"{name}: {creation_time} {delta_time}")
            image = concatenate_images(lods)
            if questionable:
                concatenate_images(lods).show()
                # input()
            print()
            image.save(f"{join(lodset_directory, full_name)}.png")

    # new_lodsets = {}

    # embed()

    # Loop over full-size filenames and identify new lodsets
    # try:
    #     for full_name, full_datum in data[1.0].items():
    #         full_image = Image.fromarray(full_datum)
    #         lods = deepcopy(known_lodsets.get(full_name, {}))
    #         lods[1.0] = full_name
    #         print(f"{full_name}:")
    #         update = False
    #         decision = ""
    #         for size in [0.5, 0.25, 0.125]:
    #
    #             # Shrink full-size image LOD size
    #             shrunk_image = full_image.resize(
    #                 sizes[size], resample=Image.LANCZOS)
    #             shrunk_datum = np.array(shrunk_image)
    #
    #             if size in lods:
    #                 # try:
    #                 assigned_datum = data[size][lods[size]]
    #                 # except KeyError:
    #                 #     embed()
    #                 assigned_score = ssim(shrunk_datum, assigned_datum,
    #                                       multichannel=True)
    #                 decision += "y"
    #                 print(f"    {size:5.3f}: {assigned_score:4.2f}  "
    #                       f"{lods[size]}")
    #             else:
    #                 # Find most similar LOD image
    #                 best_name = None
    #                 best_score = 0
    #                 for name, datum in data[size].items():
    #                     if name in known_lores:
    #                         continue
    #                     score = ssim(shrunk_datum, datum, multichannel=True)
    #                     if score > best_score:
    #                         best_name = name
    #                         best_score = score
    #                 if best_name is not None:
    #                     lods[size] = best_name
    #                 if 1.0 > best_score and best_score > threshold:
    #                     decision += "y"
    #                     print(f"  + {size:5.3f}: {best_score:4.2f}  "
    #                           f"{best_name}")
    #                     update = True
    #                 else:
    #                     decision += "n"
    #                     print(f"    {size:5.3f}: {best_score:4.2f}  "
    #                           f"{best_name}")
    #         if update:
    #             concatenate_images(lods).show()
    #             decision = input_prefill("Accept assignments?: ", decision)
    #             del lods[1.0]
    #             for d, size in zip(decision, [0.5, 0.25, 0.125]):
    #                 if d == "n":
    #                     if size in lods:
    #                         del lods[size]
    #             new_lodsets[full_name] = lods
    # except KeyboardInterrupt:
    #     embed()
    #
    # for full_name, lods in new_lodsets.items():
    #     print(f"{full_name}:")
    #     for size in [0.5, 0.25, 0.125]:
    #         if size in lods:
    #             print(f"  {size}: {lods[size]}")
