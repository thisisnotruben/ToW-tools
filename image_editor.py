#!/usr/bin/env python3

"""
Ruben Alvarez Reyes
"""

import sys
import os.path
from PIL import Image, ImageFont, ImageDraw, ImageChops
from enum import Enum, unique


_font_dir = "fonts"
_font_dir = os.path.join(os.path.dirname(sys.argv[0]), _font_dir)


@unique
class Color(Enum):
    RED = (255, 0, 0, 255)
    GREEN = (0, 255, 0, 255)
    BLUE = (0, 0, 255, 255)
    MAGENTA = (255, 0, 255, 255)
    YELLOW = (255, 255, 0, 255)
    CYAN = (0, 255, 255, 255)
    DARK_GREY = (21, 21, 21, 255)


@unique
class Font(Enum):
    MAGO = ImageFont.truetype(os.path.join(_font_dir, "mago1.ttf"), 16)


class ImageEditor:

    @staticmethod
    def get_frame_size(img_width, img_height, hvframes=()):
        width = int(img_width / hvframes[0])
        height = int(img_height / hvframes[1])
        return width, height

    @staticmethod
    def fill_bg(input_path, output_path, color=Color.DARK_GREY.value):
        """Fills image with background color"""
        with Image.open(input_path) as img:
            backgroud = Image.new("RGBA", (img.width, img.height), color)
            backgroud.paste(img, (0, 0), img)
            backgroud.save(output_path)
            backgroud.close()

    @staticmethod
    def text_grid(input_path, output_path, hvframes=(), text_color=Color.MAGENTA.value, text_font=Font.MAGO.value, offset=(1, 1), start_count=0):
        """Enumerates image in a grid like fashion per frame"""
        with Image.open(input_path) as img:
            draw = ImageDraw.Draw(img)
            width, height = get_frame_size(img.width, img.height, hvframes)
            count = start_count
            for y in range(0, img.height, height):
                for x in range(0, img.width, width):
                    draw.text((x + offset[0], y + offset[1]), str(count), fill=text_color, font=text_font)
                    count += 1
            img.save(output_path)

    @staticmethod
    def line_grid(input_path, output_path, hvframes=(), color=Color.GREEN.value, line_width=1, offset=(1, 1)):
        """Draws a grid on the image."""
        with Image.open(input_path) as img:
            draw = ImageDraw.Draw(img)
            width, height = get_frame_size(img.width, img.height, hvframes)
            for x in range(0, img.width, width):
                line = ((x + offset[0], 0), (x + offset[0], img.height))
                draw.line(line, color, line_width)
            for y in range(0, img.height, height):
                line = ((0, y + offset[1]), (img.width, y + offset[1]))
                draw.line(line, color, line_width)
            img.save(output_path)

    @staticmethod
    def crop_frame(input_path, output_path, hvframes=(), frame=()):
        """Crops Image; hvframes/frame parameters are tuples, frame starts at 0"""
        with Image.open(input_path) as img:
            width, height = get_frame_size(img.width, img.height, hvframes)
            x = width * frame[0]
            y = height * frame[1]
            sprite = img.crop((x, y, x + width, y + height))
            final = Image.new("RGBA", (width, height))
            final.paste(sprite, (0, 0))
            final.save(output_path)
            final.close()

    @staticmethod
    def create_overlay(input_path, output_path, overlay_color):
        image = Image.open(input_path, "r")
        overlay = Image.new("RGBA", image.size, overlay_color)
        out = ImageChops.multiply(image, overlay)
        out.save(output_path)

