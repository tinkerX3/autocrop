#!/usr/bin/env python
import sys, os
import argparse
import re

from PIL import Image
from PIL import ImageFilter
import numpy as np

from skimage.filter.rank import entropy as _entropy
from skimage.morphology import disk
from skimage.util import img_as_ubyte

HELP_MSG = "Invalid input '{}', see --help for usage error."

SUMMATION_KERNEL_SIZE = 50
ENTROPY_MEAN_THRESHOLD1 = 5
ENTROPY_MEAN_THRESHOLD2 = 4
ENTROPY_STD_THRESHOLD = 0.8


def _valid_numbers(values):
    try: return [int(i) for i in re.compile(r'\d+').findall(values)]
    except ValueError:
        raise argparse.ArgumentTypeError(HELP_MSG.format(values))


def _valid_size(values):
    width, height = _valid_numbers(values)
    if not width > 0 < height:
        sys.exit(HELP_MSG.format(values))
    return _valid_numbers(values)


def _valid_featured(values):
    x1, y1, x2, y2 = _valid_numbers(values)
    if not x1 < x2 and y1 < y2:
        sys.exit(HELP_MSG.format(values))
    return _valid_numbers(values)


#def _valid_input(filepath):
#    if not os.path.isfile(filepath):
#        sys.exit("File '{}' doesn't exist".format(filepath))
#    return filepath


def _valid_output(filepath):
    dir, file = os.path.split(filepath)
    if dir and not os.path.exists(dir):
        sys.exit(HELP_MSG.format(filepath))
    return filepath


def center_rect(featured, size):
    """Return a tuple of cropping rect coordinates (x1, y1, x2, y2)"""
    x1, y1, x2, y2 = featured
    width, height = size
    dx = abs(x2 - x1 - width) // 2
    dy = abs(y2 - y1 - height) // 2
    return x1 - dx, y1 - dy, x2 + dx, y2 + dy


def readjust_rect(featured, size):
    """
    If rect is outside the bounds of an image, clip the rect in the
    appropriate places and return a tuple with new coordinates
    (x1, y1, x2, y2)
    """
    x1, y1, x2, y2 = featured
    width, height = size
    def _clip(v1, v2, size):
        return (max(0, v1 + (size - max(size, v2))),
                min(v2 - min(0, v1), size))
    x1, x2 = _clip(x1, x2, width)
    y1, y2 = _clip(y1, y2, height)
    return x1, y1, x2, y2


def crop_image(image, outputfile, box):
    """Crop and save an image in a file"""
    region = image.crop(box)
    region.save(outputfile)


def grayscale(im):
    """Conver an image to a grayscale"""
    return im.convert('L')


def ubyte(im):
    """Convert an image to 8-bit unsigned integer format."""
    return img_as_ubyte(im)


def entropy(A, disk_size=5):
    """
    Returns the entropy [1]_ computed locally. Entropy is computed using
    base 2 logarithm i.e. the filter returns the minimum number of bits
    needed to encode local greylevel distribution.
    """
    return _entropy(A, disk(disk_size))


def blur(im, radius=10):
    """Gaussian blur filter"""
    return im.filter(ImageFilter.GaussianBlur(radius))


def choose_entropy(im):
    """ Choose an appropriate entropy based on the thresholds"""
    A = np.array(grayscale(im))
    H = entropy(A)
    if (H.mean() > ENTROPY_MEAN_THRESHOLD1 or
        H.mean() > ENTROPY_MEAN_THRESHOLD2 and
        H.std() < ENTROPY_STD_THRESHOLD):
        print('Blured lines')
        return entropy(np.array(grayscale(blur(im))))
    else:
        return H


def convolve(A, kernel_size=SUMMATION_KERNEL_SIZE):
    """
    Return convolved value by sliding a kernel through an array.
    """
    kernel = np.ones(kernel_size)

    def _conv(A):
        return np.convolve(A.ravel(), kernel, mode='same').reshape(A.shape).T

    return _conv(_conv(A))


def max_position(A):
    """Return indices where A has maximum value."""
    return np.unravel_index(A.argmax(), A.shape)


def optimal_output_rect(A, thresh_std=1.6):
    SAME_INTERVAL_DISTANCE = 30
    B = A.copy()
    B[B < B.mean() + thresh_std*B.std()] = 0

    def _optimal_interval(axis_sum):
        indexes = axis_sum.nonzero()[0]
        prev = start = indexes[0]
        intervals = []
        for i in indexes:
            if i - prev > SAME_INTERVAL_DISTANCE:
                intervals.append((start, prev))
                start = i
            prev = i
        intervals.append((start, prev))
        # ...
        def _range(interval):
            return interval[1] - interval[0]
        intervals.sort(key=_range, reverse=True)
        # ...
        for i in range(len(intervals) - 1):
            if _range(intervals[i]) / _range(intervals[i+1]) > 1.25:  # TODO
                break
        intervals = intervals[:i + 1]
        # ...
        intervals.sort(key=lambda i: axis_sum[i[0]:i[1] + 1].sum(), reverse=True)
        return intervals[0]

    x1, x2 = _optimal_interval(B.sum(0))
    y1, y2 = _optimal_interval(B.sum(1))
    margin = (.1 * np.array(A.shape)).astype(int)
    return x1 - margin[0], y1 - margin[1], x2 + margin[0], y2 + margin[1]


def main():
    parser = argparse.ArgumentParser(description="Image auto-cropper")
    parser.add_argument("-s", "--size", type=_valid_size,
                        metavar="WxH",
                        help="ouput image size")
    parser.add_argument("-f", "--featured", type=_valid_featured,
                        metavar="X1,Y1,X2,Y2",
                        help=("coordinates of the important part of the image;"
                              "X1 < X2, Y1 < Y2; (0,0) = top-left corner"))
    parser.add_argument("-i", "--input", # type=_valid_input,
                        metavar="FILE",
                        help="path/to/image")
    parser.add_argument("-o", "--output", type=_valid_output,
                        metavar="FILE",
                        help="path/to/output")
    args = parser.parse_args()

    #print(args)

    im_orig = Image.open(args.input)

    if args.featured:
        x1, y1, x2, y2 = args.featured
        args.size = args.size or (x2-x1, y2-y1)
        rect = center_rect(args.featured, args.size)
        rect = readjust_rect(rect, im_orig.size)
        crop_image(im_orig, args.output, rect)
    else:
        H = choose_entropy(im_orig)
        HC = convolve(H)
        i, j = max_position(HC)
        if args.size:
            rect = center_rect((j, i, j, i), args.size)
        else:
            rect = optimal_output_rect(HC)
        rect = readjust_rect(rect, im_orig.size)
        crop_image(im_orig, args.output, rect)
if __name__ == '__main__':
    main()
