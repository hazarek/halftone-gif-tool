import numpy as np
from os import mkdir, path 
from shutil import rmtree
from PIL import Image
from tools import makelut, normalize, openora



def palette_from_layers(layers):
    palette = np.empty([len(layers), 3])
    for x in range(len(layers)):
        palette[x] = layers[x][0,0][:-1] #sol üst piksel rengi
    palette = palette.astype("uint8")
    return palette

class Halftone():


    """halftone generator from psd"""
    def __init__(self, ora, step=1, period=16, waveform="sawtooth", adjust=False):
            self.layers = openora(ora)
            # print(self.layers)
            self.height_map = self.layers[-1][:, :, 0]
            self.layers.pop()
            self.palette = palette_from_layers(self.layers)
            self.h = self.layers[0].shape[1]
            self.w = self.layers[0].shape[0]
            self.layercount = len(self.layers)
            self.levelsteps = np.linspace(255, 255 / self.layercount, self.layercount).astype("uint8")
            # prepare layers
            for i in range(len(self.layers)):
                if (i == 0):
                    self.layers[i] = self.layers[i][:, :, :3] #convert background layer to RGB
                else:
                    if adjust == True:
                        self.layers[i] = normalize(self.layers[i][:, :, 3], bounds=(0, self.levelsteps[i]))
                    else:
                        self.layers[i] = self.layers[i][:, :, 3]

            self.lut = makelut(step=step, period=period, waveform=waveform)
            self.total_frames = self.lut.shape[0]
            # self.total_frames = int(256 / repeat)

    def savepalette(self, path):
        self.palette = self.palette.reshape((self.palette.shape[0], 1, self.palette.shape[1]))
        impalet = Image.fromarray(self.palette)
        impalet = impalet.resize((int(impalet.width * 64), int(impalet.height * 64)))
        impalet = impalet.rotate(90, expand=True)
        impalet.save(path)

    def get_frame(self, frame_no):
        pattern = np.take(self.lut[frame_no], self.height_map)
        frame = self.layers[0].copy()  # base layer

        for i in range(1, len(self.layers)):
            blend = (self.layers[i].astype("int16") + pattern.astype("int16")) / 2
            mask = (blend > 128)
            frame[mask] = self.palette[i]
        return frame

    def saveframe(self, frame_no):
        frame = self.get_frame(frame_no)
        Image.fromarray(frame).save(str(frame_no) + "frame.png")

    def saveframes(self):
        folder = 'frames'
        if not path.exists(folder):
            mkdir(folder)
        if path.exists(folder):
            rmtree(folder)
            mkdir(folder)

        for i in range(self.total_frames):
            Image.fromarray(self.get_frame(i)).save('frames/' + str(i) + ".png")

    def savedems(self):
        folder = 'dem_frames'
        if not path.exists(folder):
            mkdir(folder)
        if path.exists(folder):
            rmtree(folder)
            mkdir(folder)
        for i in range(self.total_frames):
            pattern = np.take(self.lut[i], self.height_map)
            Image.fromarray(pattern).save('dem_frames/' + str(i) + ".png")

    def info(self):
        index = 0
        print("input_img_size: ", self.input_img_size)
        print("input_dem_size: ", self.input_dem_size)
        print("new_dem_size: ", (self.height_map.shape[1], self.height_map.shape[0]))
        for i in self.layers:
            print("layer ", index, " : ", (i.shape[1], i.shape[0]), "color: ", self.palette[index] )
            index += 1


    def savegif(self, filename, scale=0.50, miliseconds=64, colour=256,sampling=3):
        # bicubic = 3
        # lanczos = 1
        gifa = []
        size = (round(self.h * scale), round(self.w * scale))
        print(size, type(size))
        for x in range(self.total_frames):
            frm = Image.fromarray(self.get_frame(x))
            frm = frm.resize(size, resample=sampling)
            # frm.thumbnail(size )
            frm = frm.convert(mode="P", matrix=None, dither=None, palette=Image.ADAPTIVE, colors=colour)
            gifa.append(frm)
        # duration 100 milliseconds gives 10 frames per second
        gifa[0].save(filename, save_all=True, append_images=gifa[1:], dither=None, optimize=False, duration=miliseconds, loop=0)


    def savewebp(self, filename, scale=0.50, miliseconds=64):
        webpa = []
        size = (round(self.h * scale), round(self.w * scale))
        print(size, type(size))
        for x in range(self.total_frames):
            frm = Image.fromarray(self.get_frame(x))
            # frm = frm.resize(size)
            frm.thumbnail(size,resample=Image.BICUBIC)
            webpa.append(frm)
        webpa[0].save(filename, save_all=True,
                                kmax=1,
                                append_images=webpa[1:],
                                lossless=True,
                                method=1,
                                quality=50,
                                allow_mixed=False,
                                minimize_size=True,
                                duration=miliseconds,
                                loop=0,
                                )

