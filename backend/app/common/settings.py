__author__ = "Mark Diamantino Caribé"

import numpy as np

ORIGINAL_IMAGE_PATH_DOES_NOT_EXISTS = -601
OUTPUT_IMAGE_PATH_DOES_NOT_EXISTS = -602
COULD_NOT_DECRYPT = -101

SALT_LEN = 32
DK_LEN = 32
COUNT = 100000
QUANTIZATION_TABLE = np.array([[16, 11, 10, 16, 24, 40, 51, 61],
                               [12, 12, 14, 19, 26, 58, 60, 55],
                               [14, 13, 16, 24, 40, 57, 69, 56],
                               [14, 17, 22, 29, 51, 87, 80, 62],
                               [18, 22, 37, 56, 68, 109, 103, 77],
                               [24, 35, 55, 64, 81, 104, 113, 92],
                               [49, 64, 78, 87, 103, 121, 120, 101],
                               [72, 92, 95, 98, 112, 100, 103, 99]])
LENGTH_MSG_SEPARATOR = 'ï'
MAX_BITS_TO_ENCODE_LENGTH = 48

P_HORIZONTAL_FLIP = 0.5  # horizontally flip 50% of all images
P_VERTICAL_FLIP = 0.2  # vertically flip 20% of all images

# crop images by -5% to 10% of their height/width
MIN_CROP = -0.05
MAX_CROP = 0.1

# scale images to 80-120% of their size, individually per axis
MIN_SCALE = 0.8
MAX_SCALE = 1.5

# translate by -20 to +20 percent (per axis)
MIN_TRANSLATE = 0.2
MAX_TRANSLATE = 0.2

# rotate by -45 to +45 degrees
MIN_ROTATION = -20
MAX_ROTATION = 20

# shear by -16 to +16 degrees
MIN_SHEAR = -10
MAX_SHEAR = 10

# blur images with a sigma between 0 and 3.0
MIN_BLUR_SIGMA = 0
MAX_BLUR_SIGMA = 3.0

# blur image using local means with kernel sizes between 2 and 7
MIN_LOCAL_BLUR_SIZE = 2
MAX_LOCAL_BLUR_SIZE = 7

# sharpen images
MIN_SHARPEN_ALPHA = 0
MAX_SHARPEN_ALPHA = 1.0

# emboss images
MIN_EMBOSS_ALPHA = 0
MAX_EMBOSS_ALPHA = 1.0

# Blending factor of the edge image for edge detection
MIN_EDGE_DETECTION_ALPHA = 0.5
MAX_EDGE_DETECTION_ALPHA = 1.0

# Dropout : randomly remove up to 10% of the pixels
MIN_DROPOUT = 0.01
MAX_DROPOUT = 0.05

# CoarseDropout : Augmenter that sets rectangular areas within images to zero
MIN_COARSE_DROPOUT = 0.01
MAX_COARSE_DROPOUT = 0.1

# Invert color channels
P_INVERSION = 0.1

# change brightness of images (by -10 to 10 of original value)
MIN_BRIGHTNESS_PURC = -5
MAX_BRIGHTNESS_PURC = 15

# change hue and saturation
MIN_HUE_SATURATION = -20
MAX_HUE_SATURATION = 20

# improve or worsen the contrast
MIN_CONTRAST = 0.5
MAX_CONTRAST = 2.0

# Superpixels : Completely or partially transform images
# to their superpixel representation.
MIN_SUPERPIXELS_PER_IMAGE = 1
MAX_SUPERPIXELS_PER_IMAGE = 10
# Replace each superpixel with a probability between 0 and 100%
# (sampled once per image) by its average pixel color.
MIN_P_REPLACE_SUPERPIXEL = 0
MAX_P_REPLACE_SUPERPIXEL = 0.1

# PiecewiseAffine : Apply affine transformations
# that differ between local neighbourhoods.
MIN_PIECEWISE_SCALE = 0.01
MAX_PIECEWISE_SCALE = 0.05

# PerspectiveTransform : Apply random four point perspective transformations to images.
MIN_PERSP_TRANSF_SCALE = 0.01
MAX_PERSP_TRANSF_SCALE = 0.1
