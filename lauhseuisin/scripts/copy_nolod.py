#!python
from itertools import chain
from os import listdir, remove
from os.path import isfile, expandvars, basename, splitext
from shutil import copyfile, copy2

from lauhseuisin.sorters import TextImageSorter

import yaml

dump_directory = expandvars(
    "$HOME/.local/share/citra-emu/dump/textures/000400000008F900")
nolod_directory = expandvars("$HOME/Documents/Zelda/1x_nolod")
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
known_lores = set(chain.from_iterable(
    [a.values() for a in known_lodsets.values() if a is not None]))


def get_name(filename: str) -> str:
    return splitext(basename(filename))[0]


for filename in listdir(nolod_directory):
    print(filename)
    remove(f"{nolod_directory}/{filename}")

for name in [get_name(f) for f in listdir(dump_directory)]:
    if name in known_actor:
        continue
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
    kind = TextImageSorter.get_image_type(f"{dump_directory}/{name}.png")
    if kind in ["shadow", "text", "time_text", "large_text"]:
        continue
    print(name)
    copy2(f"{dump_directory}/{name}.png", f"{nolod_directory}/{name}.png")
# known = [get_name(f) for f in listdir(dump_directory)]
# for name in [get_name(f) for f in listdir(henriko_directory)]:
#     if name not in known:
#         print(name)
#         copyfile(f"{henriko_directory}/{name}.png", f"{nolod_directory}/{name}.png")
