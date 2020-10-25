# halftone-gif-tool by hazarek is licensed under CC BY-NC-SA 4.0.
# To view a copy of this license, visit creativecommons.org/licenses/by-nc-sa/4.0
# github.com/hazarek
# github.com/hazarek/halftone-gif-tool

from halftone import Halftone as hf


test = hf("input.ora", step=1, period=15, waveform="sawtooth", adjust=False)
test.savegif("demo.gif", scale=0.3, miliseconds=60, colour=256, sampling=3)

# test.savewebp("wp2.webp",scale=0.5, miliseconds=60)
