import subprocess
from math import log10
from os import path

import cv2
import numpy


def image_exists(path_):
    return path.exists(path_) and path.isfile(path_)


def is_a_good_place(path_):
    return path.exists(path.dirname(path_))


def get_image(img_path: str) -> numpy.ndarray:
    """
    Loads image into memory as a OpenCV image.
    :param img_path: Path to image [STR]
    :return: OpenCV grayscale image [NUMPY NDARRAY]
    """
    img = cv2.imread(img_path, cv2.IMREAD_UNCHANGED)
    if img is None:
        raise ValueError("Image was not found!")
    return img


def string_to_binary(string_text: str) -> list:
    """
    Converts utf-8 text to its binary form (8 bit per character).
    :param string_text: UTF-8 text [STRING]
    :return: Array containing each bit of the binary form of each character
             [LIST OF STRINGS]
    """
    map_of_binary_str = map(lambda x: str(format(ord(x), '08b')),
                            string_text)
    return [item for sublist in map_of_binary_str for item in sublist]


def extract_block_from_image(img: numpy.ndarray,
                             block_index: int,
                             block_size=8) -> numpy.ndarray:
    """
    Getter for the 'block_index'th sub image of 'block_size' from an 'img'age
    :param img: Original image [NUMPY NDARRAY]
    :param block_index: Index of the sub image to extract [INT]
    :param block_size: Size of the sub image to extract [INT]
    :return: Sub image [NUMPY NDARRAY]
    """
    width = len(img[0])
    i = 8 * (block_index % (width // block_size))
    j = 8 * (block_index // (width // block_size))
    return img[j:j + block_size, i:i + block_size]


def get_YCrCb_from_original_img(img: numpy.ndarray) -> tuple:
    """
    Split image into its color spaces Y, Cr, Cb where
    - Y is the luma component of the color.
    - Cb and Cr is the blue component and red component related to the chroma component
    :param img: Original image [NUMPY NDARRAY]
    :return: Tuple of the three channels
    """
    YCrCbImage = cv2.cvtColor(img, cv2.COLOR_BGR2YCR_CB)
    y, cr, cb = cv2.split(YCrCbImage)
    return (y, cr, cb)


def get_original_img_from_YCrCb(y: numpy.ndarray,
                                cr: numpy.ndarray,
                                cb: numpy.ndarray) -> numpy.ndarray:
    """
    Given the color space YCbCr, recompose the image to original format.
    :param y: Luma component of the color [NUMPY NDARRAY]
    :param cr: Red component related to chroma [NUMPY NDARRAY]
    :param cb: Blue component related to chroma [NUMPY NDARRAY]
    :return: Recomposed image from color space [NUMPY NDARRAY]
    """
    ycrcb_format_img = cv2.merge((y, cr, cb))
    standard_format_img = cv2.cvtColor(ycrcb_format_img, cv2.COLOR_YCR_CB2BGR)
    return standard_format_img


# COMPARISON UTILS ===================================================================

def compute_mean_square_error(cover_image_path: str, stego_image_path: str) -> float:
    """
    Performs a byte by byte comparison of the two images.
    :param cover_image_path: Path to cover image [STR]
    :param stego_image_path: Path to stego image [STR]
    :return: MSE unit:dB [FLOAT]
    """
    cover_image = cv2.imread(cover_image_path, cv2.IMREAD_GRAYSCALE)
    stego_image = cv2.imread(stego_image_path, cv2.IMREAD_GRAYSCALE)
    diff = numpy.sum(
        (cover_image.astype("float") - stego_image.astype("float")) ** 2)
    err = numpy.divide(diff, float(cover_image.shape[0] * cover_image.shape[1]))
    return err


def compute_peak_signal_to_noise_ratio(mean_square_error: float) -> float:
    """
    PSNR is used to measure the quality of reconstruction
    of lossy compression techniques.
    Larger the PSNR, the better the quality (less distortion).
    :param mean_square_error: MSE unit:dB [FLOAT]
    :return: Ratio of the maximum signal to noise in the stego image [dB]
    """
    return 10 * log10((255 ** 2) / mean_square_error)


def compare_images(cover_image_path: str, stego_image_path: str) -> tuple:
    """
    Used to compare cover image (before embedding message)
    and stegoimage (after message hidden).
    It returns two comparison parameters:
    1 - Mean square error: byte by byte comparison of the two images [FLOAT]
    2 - PSNR (measures the quality of reconstruction of lossy compression) [FLOAT]
    :param cover_image_path: Path to cover image [STR]
    :param stego_image_path: Path to stegoimage [STR]
    :return: Tuple of the mean square error and the peak signal to noise ratio [TUPLE]
    """
    mean_square_error = compute_mean_square_error(cover_image_path, stego_image_path)
    peak_signal_to_noise_ratio = compute_peak_signal_to_noise_ratio(mean_square_error)
    return (mean_square_error, peak_signal_to_noise_ratio)


# CLI UTILS ===========================================================================

def shred_traces(path_of_file_to_delete: str):
    """
    Securely erases files.
    :param path_of_file_to_delete: Paths to files to delete
    """
    subprocess.check_call(['shred', '-zn', '10', '-u', path_of_file_to_delete])
