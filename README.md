[![Build Status](https://travis-ci.org/KarlTDebiec/PipeScaler.svg?branch=master)](https://travis-ci.org/KarlTDebiec/PipeScaler)
[![Coverage Status](https://coveralls.io/repos/github/KarlTDebiec/PipeScaler/badge.svg?branch=master&service=github)](https://coveralls.io/github/KarlTDebiec/PipeScaler?branch=master)

PipeScaler is a tool for increasing the resolution of collections of images. It
wraps around tools including ESRGAN, Pixelmator, potrace, pngquant, waifu, and
xbrz, and allows them to be applied in a defined sequence to a batch of images.
Pipescaler supports directing images down different pipelines based on their
contents, filenames, or inclusion on a configured list.

Pipescaler may be used with any collection of images, and is currently
optimized for working with texture images dumped by Citra or TexMod.
