import os
import math
from PIL import Image
from PIL import ImageOps
from PIL import ImageFilter
from PIL import ImageFont
from PIL import ImageDraw
import argparse


class Margin:
    def __init__(self):
        self.top = 32
        self.bottom = 28
        self.vertical = 10
        self.left = 10
        self.right = 10
        self.horizontal = 10
        self.texttop = 3
        self.textbottom = 4
        self.textright = 8

MARGIN = Margin()
BORDER = 4
FONTBIG = 24
FONTSMALL = 20
IMAGEWIDTH = 800


def getimages(directory='.'):
    fs = [f for f in os.listdir(directory) if f.endswith('.jpg')]
    fs.sort()
    images = [Image.open(directory + '/' + f) for f in fs]
    return images


def averagesize(images):
    return ((sum([i.size[0] for i in images])) / len(images),
            sum([i.size[1] for i in images]) / len(images))


def resize(images):
    size = averagesize(images)
    width = IMAGEWIDTH
    height = width * size[1] / size[0]
    return [i.resize((width, height), Image.ANTIALIAS) for i in images]


def border(images):
    return [ImageOps.expand(i, border=BORDER, fill='black') for i in images]


def compose(images, columns=1):
    rows = int(math.ceil(float(len(images)) / columns))
    size = images[0].size
    m = MARGIN
    w = size[0] * columns + m.horizontal * (columns - 1) + m.left + m.right
    h = size[1] * rows + m.vertical * (rows - 1) + m.top + m.bottom
    img = Image.new('RGB', (w, h), color="white")
    index = 0
    for y in xrange(m.top,
                    h - size[1],
                    size[1] + m.vertical):
        for x in xrange(m.left,
                        w - size[0],
                        size[0] + m.horizontal):
            if index >= len(images):
                break
            img.paste(images[index], (x, y))
            index += 1
    return img


def widerstroke(images):
    newimages = []
    for image in images:
        image = image.filter(ImageFilter.MinFilter)
        image = image.filter(ImageFilter.MinFilter)
        image = image.filter(ImageFilter.BLUR)
        image = image.filter(ImageFilter.UnsharpMask)
        newimages.append(image)
    return newimages


def blackandwhite(images):
    return [image.convert('L') for image in images]


def label(image, title, url, email):
    size = image.size
    draw = ImageDraw.Draw(image)
    font = ImageFont.truetype("./fonts/Montserrat-Regular.ttf", FONTBIG)
    msg = title
    txtsize = draw.textsize(msg, font=font)
    draw.text(((size[0] - txtsize[0]) / 2, MARGIN.texttop),
              msg, "black", font=font)
    font = ImageFont.truetype("./fonts/Montserrat-Regular.ttf", FONTSMALL)
    msg = url
    txtsize = draw.textsize(msg, font=font)
    draw.text((MARGIN.left, size[1] - (txtsize[1] + MARGIN.textbottom)),
              msg, "black", font=font)

    font = ImageFont.truetype("./fonts/Montserrat-Regular.ttf", FONTSMALL)

    msg = email
    name, domain = msg.split("@")
    txtsize = draw.textsize(msg, font=font)
    msg = name
    cursor = size[0] - (MARGIN.right + MARGIN.textright + txtsize[0])
    txtsize = draw.textsize(msg, font=font)
    draw.text((cursor,
               size[1] - (txtsize[1] + MARGIN.bottom + MARGIN.vertical)),
              msg, "black", font=font)
    cursor = cursor + txtsize[0]

    msg = "@"
    txtsize = draw.textsize(msg, font=font)
    draw.text((cursor,
               size[1] - (txtsize[1] + MARGIN.bottom + MARGIN.vertical)),
              msg, "red", font=font)

    cursor = cursor + txtsize[0]
    msg = domain
    txtsize = draw.textsize(msg, font=font)
    draw.text((cursor,
               size[1] - (txtsize[1] + MARGIN.bottom + MARGIN.vertical)),
              msg, "black", font=font)
    return image

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Tile images and add labels.')
    parser.add_argument('-d', '--directory', default='.')
    parser.add_argument('-t', '--title', default='FunesLab al rescate')
    parser.add_argument('-u', '--url', default='http://funeslab.com')
    parser.add_argument('-e', '--email', default='hola@funeslab.com')
    parser.add_argument('-c', '--columns', default=1, type=int)
    parser.add_argument('-r', '--rgb', action='store_true')
    parser.add_argument('-o', '--output', default='OUTPUT.JPG')
    args = parser.parse_args()
    images = getimages(args.directory)
    images = widerstroke(images)
    if not args.rgb:
        images = blackandwhite(images)
    images = resize(images)
    images = border(images)
    image = compose(images, columns=args.columns)
    image = label(image, args.title, args.url, args.email)
    image.save(args.output)
