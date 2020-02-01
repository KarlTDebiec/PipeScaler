#!/usr/bin/python

from os import R_OK, access, listdir, W_OK
from os.path import expandvars, isdir, isfile, basename, dirname

import numpy as np
import yaml
from PIL import Image, UnidentifiedImageError
from imgcat import imgcat
from IPython import embed
from collections import OrderedDict

import h5py


class ZeldaUpsaler(object):

    # region Builtins

    def __init__(self, conf_file="conf.yaml"):

        # Read configuration
        if not (isfile(conf_file) and access(conf_file, R_OK)):
            raise ValueError()
        with open(conf_file, "r") as f:
            conf = yaml.load(f, Loader=yaml.SafeLoader)
        self.dump_directory = conf["Dump"]
        self.cache_file = conf["Cache"]

    def __call__(self):

        # Load cache
        self.load_cache()

        # Load confirmed image cache
        #   HDF5 file with two tables:
        #       images/confirmed/filename (Nx36 str)
        #       images/confirmed/text (N str)
        #   Reconstruct data structures
        #       confirmed_images (dict):
        #           Keys are filenames (str)
        #           Values are text (str)

        # Load unconfirmed image cache
        #   HDF5 file with three tables:
        #       images/unconfirmed/filename (Nx36 str)
        #       images/unconfirmed/image (Nx256x256 uint8)
        #   Reconstruct data structures
        #       unconfirmed_images (dict):
        #           Keys are filenames (str)
        #           Values are list of character images in bytes

        # Review all existing images
        for i, file in enumerate(listdir(self.dump_directory)):
            if not (self.is_text_image(f"{self.dump_directory}/{file}")):
                continue

            text_data = np.array(Image.fromarray(np.array(
                Image.open(f"{self.dump_directory}/{file}"))[:, :, 3]))
            for x in range(16):
                for y in range(16):
                    char_data = text_data[x * 16:(x + 1) * 16,
                                y * 16:(y + 1) * 16]
                    if (char_data == 255).sum() != 256:
                        if char_data.tobytes() not in self.chars:
                            self.chars[char_data.tobytes()] = ("", False)
            print(i, file, len(self.chars))

        for char, (assignment, confirmed) in self.chars.items():
            if not confirmed:
                image = Image.fromarray(
                    np.frombuffer(char, dtype=np.uint8).reshape(16, 16))
                print(np.frombuffer(char, dtype=np.uint8).reshape(16, 16))
                imgcat(image.resize((160, 160)))
                try:
                    assignment = input("Assignment:")
                    if assignment != "":
                        self.chars[char] = (assignment, True)
                except KeyboardInterrupt:
                    break

        # Save cache
        self.save_cache()

    # endregion

    # region Properties

    @property
    def cache_file(self):
        if not hasattr(self, "_cache_file"):
            self._cache_file = None
        return self._cache_file

    @cache_file.setter
    def cache_file(self, value):
        value = expandvars(value)
        if isfile(value):
            if not (access(value, R_OK) and access(value, W_OK)):
                raise ValueError()
        elif isdir(dirname(value)):
            if not (access(dirname(value), R_OK)
                    and access(dirname(value), W_OK)):
                raise ValueError()
        else:
            raise ValueError
        self._cache_file = value

    @property
    def chars(self):
        if not hasattr(self, "_chars"):
            self._chars = OrderedDict()
        return self._chars

    @chars.setter
    def chars(self, value):
        if not (isinstance(value, OrderedDict)):
            raise ValueError()
        self._chars = value

    @property
    def dump_directory(self):
        if not hasattr(self, "_dump_directory"):
            raise ValueError()
        return self._dump_directory

    @dump_directory.setter
    def dump_directory(self, value):
        value = expandvars(value)
        if not (isdir(value) and access(value, R_OK)):
            raise ValueError()
        self._dump_directory = value

    @property
    def unconfirmed_images(self):
        if not hasattr(self, "_unconfirmed_images"):
            self._unconfirmed_images = {}
        return self._unconfirmed_images

    @unconfirmed_images.setter
    def unconfirmed_images(self, value):
        if not (isinstance(value, dict)):
            raise ValueError()
        self._unconfirmed_images = value

    # endregion

    # region Public Methods

    def load_cache(self):
        with h5py.File(self.cache_file) as f:
            if "characters" in f:
                assignments = [a.decode("UTF8") for a in
                               np.array(f["characters/assignments"])]
                confirmations = np.array(f["characters/confirmations"])
                images = np.array(f["characters/images"])
                for i, a, c in zip(images, assignments, confirmations):
                    self.chars[i.tobytes()] = (a, c)

    def is_text_image(self, path):
        if basename(path).split("_")[1] != "256x256":
            return False
        try:
            rgba_data = np.array(Image.open(path))
        except UnidentifiedImageError:
            return False
        if rgba_data.shape != (256, 256, 4):
            return False
        if rgba_data[:, :, :3].sum() != 0:
            return False
        return True

    def save_cache(self):
        with h5py.File(self.cache_file) as f:
            # Save characters
            if "characters" in f:
                del f["characters"]
            assignments = [v[0].encode("UTF8") for v in self.chars.values()]
            f.create_dataset("characters/assignments",
                             data=assignments,
                             dtype="S1",
                             chunks=True,
                             compression="gzip")
            confirmations = [v[1] for v in self.chars.values()]
            f.create_dataset("characters/confirmations",
                             data=confirmations,
                             dtype=bool,
                             chunks=True,
                             compression="gzip")
            images = np.stack(
                [np.frombuffer(k, dtype=np.uint8) for k in self.chars.keys()])
            images = images.reshape((-1, 16, 16))
            f.create_dataset("characters/images",
                             data=images,
                             dtype=np.uint8,
                             chunks=True,
                             compression="gzip")

    # endregion


if __name__ == "__main__":
    ZeldaUpsaler()()
