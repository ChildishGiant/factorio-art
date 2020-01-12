#!/usr/bin/python

import argparse
from PIL import Image
from PIL import ImageOps
import base64
import zlib
import json
import pyperclip

parser = argparse.ArgumentParser()
parser.add_argument("image",
                    help="Path to the image you want to turn into a blueprint")

parser.add_argument("-d", "--dither", action='store_true',
                    help="Dither the image or not")

parser.add_argument("-i", "--invert", action='store_true')

parser.add_argument("-c", "--copy", action='store_true',
                    help="Copy the blueprint code to clipboard")

parser.add_argument("--black", default="stone-path",
                    help="What tile to use for black pixels, 'none' for no tile")

parser.add_argument("--white", default="concrete",
                    help="What tile to use for white pixels, 'none' for no tile")

parser.add_argument("--file",
                    help="Write the blueprint string to a local file")

args = vars(parser.parse_args())

jsonString = """{"blueprint":{"item":"blueprint","icons":[{"signal":{"name": "hazard-concrete","type": "item"},"index": 1}],"tiles":["""


image = Image.open(args["image"])

image = image.convert("1", dither=1 if args["dither"] else 0)

if args["invert"]:
    image = ImageOps.invert(image.convert('L'))

width, height = image.size
for i in range(width):
    for j in range(height):
        pixel = image.getpixel((i, j))

        # If there's no set white, skip white pixels
        if pixel == 255 and args["white"] == "none":
            continue
        elif pixel == 255 and args["white"]:
            jsonString += '{"name":"' + args["white"] + '","position":{"x":' + str(i-width / 2) + ',' + '"y":' + str(j-height / 2) + '}},'
            continue

        # If we're at this point, the pixel is black
        if args["black"] == "none":
            continue
        else:
            jsonString += '{"name":"' + args["black"] + '","position":{"x":' + str(i-width / 2) + ',' + '"y":' + str(j-height / 2) + '}},'
        # {"entity_number":1,"name":"transport-belt","position":{"x":0,"y":0}
        # b'{"blueprint":{"icons":[{"signal":{"type":"item","name":"transport-belt"},"index":1}],"entities":[{"entity_number":1,"name":"transport-belt","position":{"x":0,"y":0}}],"item":"blueprint","version":73017393153}}'

# remove the last comma and add closing delimiters
jsonString = jsonString[:-1] + "]}}"


# blueprint format is major version number of game (currently 0)
# followed by deflated and base 64 encoded json
compressed = zlib.compress(jsonString.encode("utf-8"), 9)
b64 = base64.b64encode(compressed)
blueprint = "0" + str(b64.decode("utf-8"))


if args["copy"]:
    pyperclip.copy(blueprint)

if args["file"]:
    with open(args["file"], "w") as write:
        write.write(blueprint)

if not args["copy"] and not args["file"]:
    print(blueprint)
