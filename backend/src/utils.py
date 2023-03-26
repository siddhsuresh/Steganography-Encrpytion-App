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
    img = cv2.imread(img_path, cv2.IMREAD_UNCHANGED)
    if img is None:
        raise ValueError("Image was not found!")
    return img

def string_to_binary(string_text: str) -> list:
    map_of_binary_str = map(lambda x: str(format(ord(x), '08b')),
                            string_text)
    return [item for sublist in map_of_binary_str for item in sublist]

def extract_block_from_image(img: numpy.ndarray,
                             block_index: int,
                             block_size=8) -> numpy.ndarray:
    width = len(img[0])
    i = 8 * (block_index % (width // block_size))
    j = 8 * (block_index // (width // block_size))
    return img[j:j + block_size, i:i + block_size]

def get_YCrCb_from_original_img(img: numpy.ndarray) -> tuple:
    YCrCbImage = cv2.cvtColor(img, cv2.COLOR_BGR2YCR_CB)
    y, cr, cb = cv2.split(YCrCbImage)
    return (y, cr, cb)

def get_original_img_from_YCrCb(y: numpy.ndarray,
                                cr: numpy.ndarray,
                                cb: numpy.ndarray) -> numpy.ndarray:
    ycrcb_format_img = cv2.merge((y, cr, cb))
    standard_format_img = cv2.cvtColor(ycrcb_format_img, cv2.COLOR_YCR_CB2BGR)
    return standard_format_img

def compute_mean_square_error(cover_image_path: str, stego_image_path: str) -> float:
    cover_image = cv2.imread(cover_image_path, cv2.IMREAD_GRAYSCALE)
    stego_image = cv2.imread(stego_image_path, cv2.IMREAD_GRAYSCALE)
    diff = numpy.sum(
        (cover_image.astype("float") - stego_image.astype("float")) ** 2)
    err = numpy.divide(diff, float(cover_image.shape[0] * cover_image.shape[1]))
    return err

def compute_peak_signal_to_noise_ratio(mean_square_error: float) -> float:
    return 10 * log10((255 ** 2) / mean_square_error)

def compare_images(cover_image_path: str, stego_image_path: str) -> tuple:
    mean_square_error = compute_mean_square_error(cover_image_path, stego_image_path)
    peak_signal_to_noise_ratio = compute_peak_signal_to_noise_ratio(mean_square_error)
    return (mean_square_error, peak_signal_to_noise_ratio)

def shred_traces(path_of_file_to_delete: str):
    subprocess.check_call(['shred', '-zn', '10', '-u', path_of_file_to_delete])
