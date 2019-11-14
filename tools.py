from io import BytesIO
from PIL import Image
from zipfile import ZipFile, ZipInfo
import numpy as np
import xml.etree.ElementTree as ET


def normalize(x, bounds=(0, 255)):
    return np.interp(x, (x.min(), x.max()), bounds).astype("uint8")


def makelut(step=1, period=16, waveform="sawtooth"):
    """
    :param str waveform: "sawtooth" or "sine"

    """
    if waveform=="sawtooth":
        gradient_count = int(256 / period)
        cm = np.linspace(0, 255, gradient_count, dtype="uint8")
        lut = np.tile(cm, period)
        luts = lut
        for x in range(step, gradient_count, step):
            luts = np.vstack([luts, np.roll(lut, x)])
        print(luts.shape[0], "frame")
        return luts

    if waveform=="sine":
        frame_count = int(round(256 / period))
        field = np.empty([1, 256])
        for n, i in enumerate(np.linspace(0, 0 * np.pi, field.shape[0])):
            for m, j in enumerate(np.linspace(0, period * np.pi, field.shape[1])):
                field[n, m] = 1 * np.sin(j)
        f = np.fft.fft2(field)
        fshift = np.fft.fftshift(f)
        f_ishift = np.fft.ifftshift(fshift)
        lut = np.abs(np.fft.ifft2(f_ishift))
        lut = normalize(lut)
        luts = lut
        for x in range(step, frame_count, step):
            luts = np.vstack([luts, np.roll(lut, x)])
        print(luts.shape[0], "frame")
        return luts


def saveora(layers, thumb, filename):

    def np2byteimage(layer):
        image = Image.fromarray(layer)
        file = BytesIO()
        image.save(file, 'png')
        file.name = 'test.png'
        file.seek(0)
        return file.read()

    def make_thumb(layer):
        image = Image.fromarray(layer)
        image.thumbnail((256, 256))
        file = BytesIO()
        image.save(file, 'png')
        file.name = 'test.png'
        file.seek(0)
        return file.read()

    def getXML(count, w, h):

        strxml = """<image version="0.0.1" w="402" h="402">
         <stack opacity="1" composite-op="svg:src-over" name="root" visibility="visible" isolation="isolate">
         </stack>
        </image>"""
        root = ET.fromstring(strxml)
        root.attrib["w"] = str(w)
        root.attrib["h"] = str(h)

        for i in reversed(range(count)):
            ET.SubElement(root[0], 'layer', src="data/layer" + str(i) + ".png", name="layer" + str(i))

        return ET.tostring(root).decode('utf-8')

    strxml = getXML(len(layers), layers[0].shape[1], layers[0].shape[0])
    in_memory = BytesIO()
    zip_file = ZipFile(in_memory, mode="w")

    thumbb = make_thumb(thumb)
    zip_file.writestr("Thumbnails/thumbnail.png", thumbb)
    zip_file.writestr("mimetype", "image/openraster")
    zip_file.writestr("stack.xml", strxml)

    for i in range(len(layers)):
        zip_file.writestr("data/layer" + str(i) + ".png", np2byteimage(layers[i]))


    #Close the zip file
    zip_file.close()
     
    #Go to beginning
    in_memory.seek(0)
     
    #read the data
    data = in_memory.read()
     
    #You can save it to disk
    with open(filename,'wb') as out:
          out.write(data)

def openora(filename):

    arsiv = ZipFile(filename, 'r')

    filelist = arsiv.namelist()
    imglist = []
    images = []

    for i in range(len(filelist)):
        if filelist[i].startswith("data"):
            imglist.append(filelist[i])

    for filename in imglist:
        image_data = arsiv.read(filename)
        fh = BytesIO(image_data)
        img = np.array(Image.open(fh))
        images.append(img)

    return images