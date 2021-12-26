#!/usr/env/bin python
"""
Main file to create PDF based on April Tag v3
Which has ignore 'b'lack ,'w'hite, 'd'ata, and 'x'ignore pattern.
Search for "layout" in this repo for examples of the bwdx pattern
"""

from math import sqrt
from pyx.canvas import canvas
from pyx.path import line, rect
from pyx.color import rgb
import numpy as np

from tag_type import AprilTagsType
from tag_aprilStandard41h12 import aprilStandard41h12
from tag_aprilCircle21h7 import aprilCircle21h7


class PdfCreator(object):
    def __init__(self, marker_type: AprilTagsType):
        self.marker_type = marker_type
        self.num_bits = self.marker_type.layout.count("d")
        self.size = int(sqrt(len(self.marker_type.layout)))
        assert self.size * self.size == len(self.marker_type.layout)
        self.marker_size = 0.2

    def convert_tag_to_array(self, tag):
        """
        Convert tag into 2D matrix containing 0 or 1
        Direct copy of https://github.com/AprilRobotics/apriltag-generation/blob/40c9f2b6c09d26001e921bfdf7576c6fab1e6b35/src/april/tag/ImageLayout.java#L199
        """
        result = np.zeros((self.size, self.size), dtype=np.uint8)

        for _ in range(4):
            result = np.rot90(result)
            # convert one-quarter of the image
            for r in range(self.size // 2 + 1):
                for c in range(r, self.size - 1 - r):
                    layout_type = self.marker_type.layout[r * self.size + c]
                    if layout_type == "d":
                        if (tag & (1 << (self.num_bits - 1))) != 0:
                            result[r][c] = 1
                        else:
                            result[r][c] = 0
                        tag = tag << 1
                    elif layout_type == "w":
                        result[r][c] = 1
                    elif layout_type == "b":
                        result[r][c] = 0
                    elif layout_type == "x":
                        result[r][c] = 2

        if self.size % 2 == 1:
            r = c = self.size // 2
            layout_type = self.marker_type.layout[r * self.size + c]
            if layout_type == "d":
                if (tag & (1 << (self.num_bits - 1))) != 0:
                    result[r][c] = 1
                else:
                    result[r][c] = 0
            elif layout_type == "w":
                result[r][c] = 1
            elif layout_type == "b":
                result[r][c] = 0
            elif layout_type == "x":
                result[r][c] = 2
        return np.rot90(result)

    def draw_tag(self, canvas: canvas, tag_id: int = 0):
        tag = self.marker_type.tags[tag_id]
        tag_array = self.convert_tag_to_array(tag)
        tag_array = np.flipud(tag_array)
        bit_size = self.marker_size / self.size
        for r in range(self.size):
            for c in range(self.size):
                if tag_array[r][c] == 1 or tag_array[r][c] == 2:
                    # Don't need to draw if it's white cell or ignored cell
                    continue
                x = c * bit_size
                y = r * bit_size
                w = h = bit_size
                canvas.fill(rect(x, y, w, h), [rgb.black])

        print(tag_array)

    def create_pdf(self):
        c = canvas()
        self.draw_tag(c, 0)
        filename = "test_%s.pdf" % self.marker_type.name
        c.writePDFfile(filename)
        print("file saved to", filename)


if __name__ == "__main__":
    # TODO: Create argparser and read config
    pdf_creator = PdfCreator(marker_type=aprilCircle21h7)
    pdf_creator.create_pdf()
