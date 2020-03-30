#!python
from itertools import chain
from os import listdir, remove
from os.path import isfile, expandvars, basename, splitext
from shutil import copyfile, copy2

from IPython import embed

from lauhseuisin.sorters import TextImageSorter
from PIL import Image
from os.path import join
import yaml

lores_directory = expandvars(
    "$HOME/.local/share/citra-emu/dump/textures/000400000008F900")
hires_directory = expandvars("$HOME/Documents/Zelda/4x_kdebiec")
debug_directory = expandvars("$HOME/Documents/Zelda/1x_debug")
henriko_directory = expandvars("$HOME/Documents/Zelda/4x_henriko")

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


def concatenate_images(filename: str) -> Image.Image:
    # Load and paste full image
    full_lores_image = Image.open(get_lores_filename(filename))
    full_lores_image = full_lores_image.resize(
        (full_lores_image.size[0] * 4, full_lores_image.size[1] * 4),
        resample=Image.NEAREST)
    concatenated_image = Image.new(
        "RGBA",
        (full_lores_image.size[0], full_lores_image.size[1] * 2))
    concatenated_image.paste(full_lores_image, (0, 0))
    if isfile(get_hires_filename(filename)):
        full_hires_image = Image.open(get_hires_filename(filename))
        concatenated_image.paste(
            full_hires_image, (0, full_lores_image.size[1]))
    return concatenated_image


def get_debug_filename(filename: str) -> str:
    return f"{join(debug_directory, filename)}.png"


def get_lores_filename(filename: str) -> str:
    return f"{join(lores_directory, filename)}.png"


def get_hires_filename(filename: str) -> str:
    return f"{join(hires_directory, filename)}.png"


def get_name(filename: str) -> str:
    return splitext(basename(filename))[0]


for filename in listdir(debug_directory):
    print(filename)
    remove(f"{debug_directory}/{filename}")

for name in [get_name(f) for f in listdir(lores_directory)]:
    if name in known_actor:
        continue
        # print(get_debug_filename(name))
        # concatenate_images(name).save(get_debug_filename(name))
    elif name in known_interface:
        continue
    elif name in known_map:
        continue
    elif name in known_skip:
        continue
    elif name in known_hires:
        continue
    elif name in known_lores:
        continue
    elif name == ".DS_Store":
        continue
    kind = TextImageSorter.get_image_type(get_lores_filename(name))
    if kind in ["shadow", "text", "time_text", "large_text"]:
        continue
    print(name)
    copy2(get_lores_filename(name), get_debug_filename(name))

# known = [get_name(f) for f in listdir(dump_directory)]
# for name in [get_name(f) for f in listdir(henriko_directory)]:
#     if name not in known:
#         print(name)
#         copyfile(f"{henriko_directory}/{name}.png", f"{nolod_directory}/{name}.png")
