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
from itertools import chain
from os import listdir, remove
from os.path import basename, expandvars, join, splitext
from typing import Optional

import numpy as np
import yaml
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

known_water = set(yaml.load("""
- tex1_128x128_09C930987A27540E_12
- tex1_128x128_17AC0716D81210BA_12
- tex1_128x128_26936F2BBF0BB1F9_12
- tex1_128x128_2ED1133F7DCED082_12
- tex1_128x128_3B652CE8614D5902_3
- tex1_128x128_4F812E353EA81C82_12
- tex1_128x128_537D9D73DD84CD39_12
- tex1_128x128_A2478BC7A69B2A1C_12
- tex1_128x128_AA38DF5CDF5BD937_12
- tex1_128x128_B7C1FAE857CB9C0C_12
- tex1_128x128_BF640DA5A4111A4E_12
- tex1_128x128_DF9C111C6FB4ECE4_12
- tex1_128x128_E9A0B4035086E610_12
- tex1_128x128_F61802D1C2E0F865_12
- tex1_32x32_0585FA3279D97187_13
- tex1_32x32_097E8AA88C226B4F_12
- tex1_32x32_100508DA4018E530_12
- tex1_32x32_2487E0A3E7D566F6_12
- tex1_32x32_2B60CAF83D700338_12
- tex1_32x32_2FBC166E53C47AC7_12
- tex1_32x32_3001A605B40C11D1_12
- tex1_32x32_31364054A6F65027_12
- tex1_32x32_39A86950E64BA3FE_12
- tex1_32x32_3B412CA00A5A300B_12
- tex1_32x32_3F6BD7AE7CBDF171_12
- tex1_32x32_43E876B03CA4CA1F_12
- tex1_32x32_47E48BFCA3F20D0D_12
- tex1_32x32_49C1276AC4689A7E_12
- tex1_32x32_520C4DBDF9F6D86A_12
- tex1_32x32_54F653328E88C9D7_12
- tex1_32x32_6588817349159AEB_12
- tex1_16x16_8D5AA6539C2863E9_12
- tex1_32x32_658CE389FCEC3992_12
- tex1_16x16_9454F71D976AEB8B_12
- tex1_32x32_681FE1C310E0C215_12
- tex1_32x32_6C9A4C016B41C888_12
- tex1_32x32_70EF838763240875_3
- tex1_32x32_7179BA8F5013E990_12
- tex1_32x32_786023AC54FB4A20_12
- tex1_32x32_7F359573DBE91D16_12
- tex1_32x32_81700F3EE2AF261E_12
- tex1_32x32_8D25F23ABEBFBA66_12
- tex1_32x32_8EF8058FC93B6D17_3
- tex1_32x32_92FA921EAA90CED6_12
- tex1_32x32_9968A52A31FBF0CE_12
- tex1_32x32_9EF54E39A0B416B0_12
- tex1_32x32_A7C4CFBC1D0DC88F_12
- tex1_32x32_AB49AA1A2A22F6B2_3
- tex1_32x32_AC8B512078D76123_12
- tex1_32x32_B43A46209BC35279_12
- tex1_32x32_C11DCF7C20B33FB2_12
- tex1_32x32_C155F4D308D20FCD_12
- tex1_32x32_C2F1C3B6E67B1DF8_12
- tex1_32x32_C7F6F9F6314E9421_12
- tex1_32x32_C89E6FBAD8710C9B_12
- tex1_32x32_CAF3F2DAEA9147CD_12
- tex1_32x32_CF564C23FA97B1E5_12
- tex1_32x32_DC4C599088449C26_12
- tex1_32x32_E23BAFFBAD8690FE_12
- tex1_32x32_ED01512EDAEE4FF8_12
- tex1_32x32_FC9AA3E8821D342D_12
- tex1_32x32_FD825BF8B73DB166_12
- tex1_64x64_030D5B706014F2EA_12
- tex1_64x64_11BE0BD9FEAE32A8_12
- tex1_64x64_13E2EFE009408956_3
- tex1_64x64_2DB1C08C894FA060_12
- tex1_64x64_3C11751C3EDDAB35_12
- tex1_64x64_4317614E90738CDC_12
- tex1_64x64_43E1F601DD74FAEB_12
- tex1_16x16_CB06971A86B4BE19_12
- tex1_64x64_4BA1C6A8FA4BFED9_12
- tex1_64x64_503E3B07E0BC7DDA_12
- tex1_32x32_749F8EEA2207AB76_12
- tex1_64x64_52AA260920F36315_12
- tex1_16x16_D5D79B605FD8C04F_12
- tex1_64x64_56DEA397DF612000_12
- tex1_64x64_114F0005E26A791F_12
- tex1_64x64_59B09F068F3312B0_12
- tex1_64x64_5A6F17899691B74F_3
- tex1_64x64_5FA6237A5B39DF51_12
- tex1_64x64_613F9A577B091D7E_12
- tex1_64x64_636DAEEE24A17728_12
- tex1_64x64_6605915523799D7A_12
- tex1_64x64_66D51E8571B49E0F_12
- tex1_64x64_6912F54E1173447A_12
- tex1_64x64_6FE34FF195D6EA77_13
- tex1_64x64_75DFB6378057B73A_12
- tex1_64x64_76AF5635E42EBD9B_12
- tex1_64x64_77377A9C56318449_12
- tex1_64x64_87040B6688EEF258_12
- tex1_64x64_8B6C90CCD54B2FF9_12
- tex1_64x64_8EB9669659A00DCD_12
- tex1_64x64_968217193A634216_12
- tex1_64x64_98955188E7DF664E_12
- tex1_64x64_A84788140383CAF4_12
- tex1_64x64_B18AB678D8BC5A9F_12
- tex1_64x64_B24DE3E7113C3609_12
- tex1_32x32_121738182ED1C30F_12
- tex1_16x16_0DADF51BB6F85630_12
- tex1_32x32_9968A52A31FBF0CE_12
- tex1_16x16_1BEACDB48A2235E5_12
- tex1_64x64_BC039CA0695F021E_12
- tex1_64x64_BD9806D0C00B08F7_12
- tex1_64x64_C7BE133416AAC3CA_3
- tex1_64x64_C85E3098892D7F1F_12
- tex1_64x64_C8B91BCEB792B997_3
- tex1_64x64_CA06D4ECC2156FB4_12
- tex1_64x64_DA372BE2BC0E14E6_12
- tex1_64x64_E2A09F7877B2BD3E_12
- tex1_64x64_E4899D219A362BF0_12
- tex1_64x64_E8580DEBB573CD9F_12
- tex1_64x64_EBC40764B2C225BD_12
- tex1_64x64_EDC157D209551AFF_12
- tex1_16x16_E0CE180D53DE5CBD_12
- tex1_64x64_F118ED87EF2CF314_12
- tex1_16x16_226592799685B741_12
- tex1_16x16_EFB8E3CDB9B7959A_12
- tex1_64x64_FD8575CCA3EAA0EA_12
- tex1_64x64_FEC49AB77EFD4F10_12
- tex1_64x64_FF4AD70E8DC370C1_12
- tex1_16x16_06C2E33287C6C54A_12
- tex1_16x16_95526E595AC53CEF_12
""", Loader=yaml.SafeLoader))

known_spider_web = set(yaml.load("""
- tex1_32x32_088B69391A3B0069_13
""", Loader=yaml.SafeLoader))


################################## FUNCTIONS ##################################
def get_name(filename: str) -> str:
    return splitext(basename(filename))[0]


def get_filename(filename: str) -> str:
    return f"{join(input_directory, filename)}.png"


def concatenate_images(full_name: str, half_name: Optional[str] = None,
                       quarter_name: Optional[str] = None,
                       eighth_name: Optional[str]=None):
    full_image = Image.open(get_filename(full_name))
    concatenated_image = Image.new(
        "RGBA", (full_image.size[0] * 4, full_image.size[1]))
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
    if eighth_name is not None:
        eighth_image = Image.open(get_filename(eighth_name))
        eighth_image = eighth_image.resize(
            full_image.size, resample=Image.LANCZOS)
        concatenated_image.paste(eighth_image, (full_image.size[0] * 3, 0))

    return concatenated_image


def load_data():
    full_data = {}
    half_data = {}
    quarter_data = {}
    eighth_data = {}
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
        elif name in known_water:
            continue
        elif name in known_spider_web:
            continue
        if full_re.match(name):
            image = Image.open(get_filename(name))
            datum = np.array(image)
            if datum.shape == (256, 256, 4):
                if datum[:, :, :3].sum() == 0:
                    continue
                y, x, _ = np.where(datum == 255)
                if (x.size > 0 and y.size > 0
                        and y.max() == 15 and x.max() < 128):
                    image.show()
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
            full_data[name] = np.array(image.convert("RGB"))
        elif half_re.match(name):
            image = Image.open(get_filename(name))
            half_data[name] = np.array(image.convert("RGB"))
        elif quarter_re.match(name):
            image = Image.open(get_filename(name))
            quarter_data[name] = np.array(image.convert("RGB"))
        elif eighth_re.match(name):
            image = Image.open(get_filename(name))
            eighth_data[name] = np.array(image.convert("RGB"))

    print(len(full_data), len(half_data), len(quarter_data), len(eigth_data))
    return full_data, half_data, quarter_data, eighth_data


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
            full_image = Image.open(get_filename(full_name)).convert("RGB")
            half_size = (full_image.size[0] // 2, full_image.size[1] // 2)
            quarter_size = (full_image.size[0] // 4, full_image.size[1] // 4)

            # Load and score lods
            lods = lodsets[full_name]
            if 0.5 in lods and 0.25 in lods:
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


#################################### MAIN #####################################
if __name__ == "__main__":
    input_directory = expandvars(
        "$HOME/.local/share/citra-emu/dump/textures/000400000008F900")
    full_size = (4, 4)
    threshold = 0.65

    # Prepare sizes and regular expressions
    half_size = (full_size[0] // 2, full_size[1] // 2)
    quarter_size = (full_size[0] // 4, full_size[1] // 4)
    full_re = re.compile(f".*_{full_size[0]}x{full_size[1]}_.*_1[23]")
    half_re = re.compile(f".*_{half_size[0]}x{half_size[1]}_.*_1[23]")
    quarter_re = re.compile(f".*_{quarter_size[0]}x{quarter_size[1]}_.*_1[23]")

    # Load in all data for half and quarter sizes
    full_data, half_data, quarter_data = load_data()

    # Loop over full-size filenames and identify new lodsets
    new_lodsets = {}
    for full_name, full_datum in full_data.items():
        full_image = Image.fromarray(full_datum)

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

        # Display results
        if half_best_score > 0.99 or quarter_best_score > 0.99:
            continue
        elif half_best_score > threshold and quarter_best_score > threshold:
            print(f"{full_name}:")
            print(f"  0.5: {half_best_name} # {half_best_score:4.2f}")
            print(f"  0.25: {quarter_best_name} # {quarter_best_score:4.2f}")
            concatenated_image = concatenate_images(
                full_name, half_best_name, quarter_best_name)
            concatenated_image.show()
            new_lodsets[full_name] = {
                0.5: half_best_name,
                0.25: quarter_best_name}
        else:
            continue

    # Print sets
    # print("\n\n")
    known_lodsets.update(new_lodsets)
    print_lodsets(known_lodsets)
