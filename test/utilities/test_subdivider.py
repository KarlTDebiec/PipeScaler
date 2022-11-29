#  Copyright 2020-2022 Karl T Debiec
#  All rights reserved. This software may be modified and distributed under
#  the terms of the BSD license. See the LICENSE file for details.
import pytest
from PIL import Image

from pipescaler.image.processors import XbrzProcessor
from pipescaler.testing import get_test_infile_path, parametrized_fixture
from pipescaler.utilities.subdivider import Subdivider

# TODO: Test both ESRGAN and Waifu2x


@parametrized_fixture(
    cls=XbrzProcessor,
    params=[
        {"scale": 6},
    ],
)
def processor(request) -> XbrzProcessor:
    return XbrzProcessor(**request.param)


@pytest.mark.parametrize(
    ("infile"),
    [
        ("RGB"),
    ],
)
def test_subdivider(infile: str, processor: XbrzProcessor) -> None:
    input_path = get_test_infile_path(infile)
    input_image = Image.open(input_path)
    # input_image = input_image.resize((96, 48))

    subdivider = Subdivider(4, 2)

    subdivided_image = subdivider.subdivide(input_image)
    subs = []
    for sub in subdivided_image.subs:
        image = processor(sub)
        subs.append(image)
    subdivided_image.subs = subs
    recomposed = subdivider.recompose(subdivided_image)

    # with subdivider(input_image) as subdivided_image:
    #     print(subdivided_image)
