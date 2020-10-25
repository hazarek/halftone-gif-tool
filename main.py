# halftone-gif-tool by hazarek is licensed under CC BY-NC-SA 4.0.
# To view a copy of this license, visit creativecommons.org/licenses/by-nc-sa/4.0
# github.com/hazarek
# github.com/hazarek/halftone-gif-tool

from halftone import Halftone as hf


test = hf("input.ora", step=1, period=12, waveform="sawtooth", adjust=False)
test.savegif("output.gif", scale=0.25, miliseconds=50, colour=128, sampling=3)

# test.savewebp("wp2.webp",scale=0.5, miliseconds=60)
