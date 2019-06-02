#!/usr/bin/python

import argparse
import sys
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

parser.add_argument("-i", "--invert", action='store_true',
                    help="Swap the tile and background")

parser.add_argument("-c", "--copy", action='store_true',
                    help="Copy the blueprint code to clipboard")

parser.add_argument("--tile", default="concrete",
                    help="What tile to use for black pixels")

parser.add_argument("--back",
                    help="What tile to use for white pixels")

parser.add_argument("--file",
                    help="Write the blueprint string to a local file")

args = vars(parser.parse_args())

jsonString = """
{
    "blueprint":
    {
        "item":"blueprint",
        "version": 68720787456,
        "icons":
        [
            {
                "signal":
                {
                    "name": "hazard-concrete",
                    "type": "item"
                },
                "index": 1
            }
        ],
        "tiles":
        [
"""


image = Image.open(args["image"])

image = image.convert("1", dither=1 if args["dither"] else 0)

if args["invert"]:
    image = ImageOps.invert(image.convert('L'))

width, height = image.size
for i in range(width):
    for j in range(height):
        pixel = image.getpixel((i, j))

        # If there's no set back, skip white pixels
        if pixel == 255 and args["back"] is None:
            continue
        elif pixel == 255:
            jsonString += '{"name":"' + args["back"] + '","position":{"x":' + str(i-width / 2) + ',' + '"y":' + str(j-height / 2) + '}},\n'
            continue

        jsonString += '{"name":"' + args["tile"] + '","position":{"x":' + str(i-width / 2) + ',' + '"y":' + str(j-height / 2) + '}},\n'
        # {"entity_number":1,"name":"transport-belt","position":{"x":0,"y":0}
        # b'{"blueprint":{"icons":[{"signal":{"type":"item","name":"transport-belt"},"index":1}],"entities":[{"entity_number":1,"name":"transport-belt","position":{"x":0,"y":0}}],"item":"blueprint","version":73017393153}}'

# remove the last comma and add closing delimiters
jsonString = jsonString[:-2] + "]}}"
# print(jsonString)

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

print(blueprint)
