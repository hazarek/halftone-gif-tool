from halftone import Halftone as hf


test = hf("input.ora", step=2, period=5, waveform="sawtooth", adjust=False)
test.savegif("output.gif",scale=0.2, miliseconds=60, colour=256,sampling=3)

# test.savewebp("wp2.webp",scale=0.5, miliseconds=60)