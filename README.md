autocrop
========

Image auto-cropper. This is [how it works][how].

[how]: http://nbviewer.ipython.org/github/tinkerX3/autocrop/blob/master/doc/autocrop.ipynb

Dependencies
------------
* Python 3
* numpy
* scikit-image
* Pillow

On a debian based distro:

```bash
sudo apt-get install python3-numpy python3-pil python3-skimage
```

Algorithm for content aware cropping
------------------------------------

1. Calculate entropy of input image.
2. Based on tresholds check if the entropy gives satisfying results. If
   not. Blur the input image, calculate entropy and continue using this
   entropy.
3. Calculate the convolution with summation kernel of fixed size.
4. Find the pixel with max value.
5. Put the pixel in the center and calculate rect with output size.
6. Readjust the rect if the original rect goes outside the boundary of
   the image.
7. Crop and save image.

Installation
------------

```
pip install git+https://github.com/tinkerX3/autocrop
```

or

```bash
git clone https://github.com/tinkerX3/autocrop.git
python3 setup.py develop  # this still is beta!
```

Usage
-----

```
usage: autocrop [-h] [-s W,H] [-f X1,Y1,X2,Y2] [-i FILE] [-o FILE]

Image cropper

optional arguments:
  -h, --help            show this help message and exit
  -s W,H, --size W,H    ouput image size
  -f X1,Y1,X2,Y2, --featured X1,Y1,X2,Y2
                        coordinates of the important part of the image;
                        X1<X2, Y1<Y2; (0,0) = top-left corner
  -i FILE, --input FILE
                        path/to/the/input/image
  -o FILE, --output FILE
                        path/to/the/output/image
```

Examples
--------

Crop image to provided size ensuring featured rectangle is included:
```bash
$ ./autocrop --size 500x500 \
             --featured 250x100x650x500 \
             --input path/to/image.png \
             --output path/to/output.png
```

Crop image to size of the featured rectangle:
```bash
$ ./autocrop --featured 250x100x650x500 \
             --input path/to/image.png \
             --output path/to/output.png
```

Crop image to provided size by automatically determining the most
important features.
```bash
$ ./autocrop --size 500x500 \
             --input path/to/image.png \
             --output path/to/output.png
```

Also determine the size of important part automatically.
```bash
$ ./autocrop --input path/to/image.png \
             --output path/to/output.png
```

