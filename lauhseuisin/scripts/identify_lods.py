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
from typing import Optional, Dict, List

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
known_lores = []
for lodset in known_lodsets.values():
    if lodset is not None:
        for lods in lodset.values():
            if isinstance(lods, str):
                lods = [lods]
            known_lores.extend(lods)
known_lores = set(known_lores)


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


def concatenate_images_2(images: List[Image.Image]) -> Image.Image:
    concatenated_image = Image.new(
        "RGBA", (images[0].size[0] * len(images), images[0].size[1]))
    for i, image in enumerate(images):
        concatenated_image.paste(image, (images[0].size[0] * i, 0))
    return concatenated_image


def input_prefill(prompt: str, prefill: str) -> str:
    def pre_input_hook() -> None:
        insert_text(prefill)
        redisplay()

    set_pre_input_hook(pre_input_hook)
    result = input(prompt)
    set_pre_input_hook()

    return result


def load_data() -> Dict[float, Dict[str, np.ndarray]]:
    data: Dict[float, Dict[str, np.ndarray]] = {
        1.0: {}, 0.5: {}, 0.25: {}, 0.125: {}}
    for name in [get_name(f) for f in listdir(lores_directory)]:
        if name in known_actor:
            continue
        elif name in known_interface:
            continue
        elif name in known_map:
            continue
        elif name in known_skip:
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
    return int(f"1{int(width):04d}{int(height):04d}{int(code, 16):022d}")


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

    for full_size in [(64, 64)]:
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

        new_lodsets = {}

        # Identify new lodsets
        try:
            full_names = list(data[1.0].keys())
            full_names.sort(key=name_sort)
            full_names = [f for f in full_names if f not in known_lodsets]
            print(len(full_names))
            for full_name in full_names:
                printed_header = False
                full_datum = data[1.0][full_name]
                full_image = Image.fromarray(full_datum)
                images = [full_image]
                lodset = {}

                # Loop over sizes
                for size in [0.5, 0.25, 0.125]:
                    shrunk_image = full_image.resize(
                        sizes[size], resample=Image.LANCZOS)
                    shrunk_datum = np.array(shrunk_image)

                    # Mipmap is not known for this image and size
                    best_name = None
                    best_score = 0
                    best_datum = None
                    for name, datum in data[size].items():
                        if name in known_lores:
                            continue
                        score = ssim(shrunk_datum, datum,
                                     multichannel=True)
                        if score > best_score:
                            best_name = name
                            best_score = score
                            best_datum = datum
                    if best_name is not None:
                        lodset[size] = [best_name]
                    if 1.0 > best_score and best_score > threshold:
                        if not printed_header:
                            print(f"{full_name}:")
                            printed_header = True
                        print(f"  {size}: {best_name} # {best_score:4.2f}")
                        images.append(
                            Image.fromarray(best_datum).resize(
                                sizes[1.0], resample=Image.LANCZOS))
                if printed_header:
                    concatenate_images_2(images).show()

        except KeyboardInterrupt:
            pass
