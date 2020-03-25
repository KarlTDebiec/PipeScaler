#!python
from itertools import chain
from os import listdir, remove
from os.path import isfile, expandvars, basename, splitext
from shutil import copyfile

from lauhseuisin.sorters import TextImageSorter

import yaml

dump_directory = expandvars(
    "$HOME/.local/share/citra-emu/dump/textures/000400000008F900")
nolod_directory = expandvars("$HOME/Documents/Zelda/1x_nolod")

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
    copyfile(f"{dump_directory}/{name}.png", f"{nolod_directory}/{name}.png")
