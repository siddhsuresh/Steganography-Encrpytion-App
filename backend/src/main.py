import glob
import subprocess
from itertools import product
import random
from warnings import warn
from os.path import abspath
from cv2 import resize, imwrite, dct, idct
import numpy as np
from bitstring import BitArray
from os.path import abspath

import warnings
warnings.filterwarnings("ignore")

import settings
from settings import SALT_LEN, DK_LEN, COUNT, COULD_NOT_DECRYPT

import utils

import imageio

class DCT:
    def __init__(self, cover_image_path, cipher_msg):
        self.__cover_image_path_ = abspath(cover_image_path)
        self.__cover_image_ = utils.get_image(cover_image_path)
        self.verify_and_apply_padding()
        self.__height_, self.__width_ = self.__cover_image_.shape[:2]
        self.__cipher_text_ = cipher_msg
        self.__bin_message_ = BitArray(bytes=cipher_msg).bin
        self.__message_length_ = len(self.__bin_message_)
        self.verify_ciphertext_size()

        self.__block_list_ = None

    # VERIFICATION METHODS ============================================================

    def verify_ciphertext_size(self):
        """
        Verifies that the length of the message to hide
        is shorter than the maximum available space in the image.
        Warning is raised if the message length is > (10% of the available capacity).
        """
        area = self.__height_ * self.__width_
        if area < 64:  # 64 -> since each quantized block is a matrix of 8x8
            raise ValueError(
                "The chosen cover image is too small (area < 64 px)")
        tot_blocks = self.__height_ * self.__width_ // 64
        if self.__message_length_ > tot_blocks:
            raise OverflowError("Cannot embed. Message is too long!")
        if self.__message_length_ > tot_blocks / 10:
            purcentage_of_occupied_storage = round(
                self.__message_length_ / tot_blocks * 100)
            warning = f"Message occupies ≈ " \
                      f"{purcentage_of_occupied_storage}% of the pic. " \
                      "A smaller text is preferred (< 10%)"
            warn(warning)

    def verify_and_apply_padding(self):
        """
        Checks and eventually resizes image applying a padding
        if any side length is not a multiple of 8.
        The original image is eventually replaced by the padded
        (with sides multiple of 8) image.
        """
        original_height, original_width = self.__cover_image_.shape[:2]
        if original_height % 8 != 0 or original_width % 8 != 0:
            self.__cover_image_ = resize(self.__cover_image_, (
                original_width + (8 - original_width % 8),
                original_height + (8 - original_height % 8)))
            imwrite(self.__cover_image_path_, self.__cover_image_)

    # BREAK/RECOMPOSE METHODS =========================================================

    @staticmethod
    def break_image_into_blocks(img: np.ndarray) -> list:
        """
        Breaks the coverimage into a sequence of 8x8 blocks,
        from top left to bottom right.
        :param img: Coverimage to break into n 8x8 blocks.
        :return: List of blocks of pixels [LIST OF NUMPY NDARRAY]
        """
        if not isinstance(img, np.ndarray):
            raise TypeError("Cannot break a non np.array image")
        height, width = len(img), len(img[0])
        return [img[j: j + 8, i: i + 8] for (j, i) in
                product(range(0, height, 8), range(0, width, 8))
                ]

    def recompose_image(self) -> np.ndarray:
        """
        Inverse of method 'breakImageIntoBlocks':
        Recompose the image from the sorted list of blocks of pixels '__block_list_'.
        :return: Re-composed image [NUMPY NDARRAY]
        """
        if len(self.__block_list_) == 0:
            raise ValueError
        full_image = np.zeros(shape=(self.__height_, self.__width_),
                              dtype=np.uint8)  # Builds empty image
        for i in range(len(self.__block_list_)):  # Filling image
            curr_col_index = 8 * (i % (self.__width_ // 8))
            curr_line_index = 8 * (i // (self.__width_ // 8))
            full_image[
            curr_line_index:curr_line_index + 8,
            curr_col_index:curr_col_index + 8
            ] = self.__block_list_[i]
        return full_image

    @staticmethod
    def quantize_block(block: np.ndarray) -> np.ndarray:
        """
        Centers values of a block, runs it through DCT func. and quantizes it.
        :param block: 8x8 block of pixels [NUMPY NDARRAY]
        :return:Quantized 8x8 block of pixels [NUMPY NDARRAY]
        """
        img_block = np.subtract(block, 128)
        dct_block = dct(img_block.astype(np.float64))
        dct_block[0][0] /= settings.QUANTIZATION_TABLE[0][0]
        dct_block[0][0] = np.round(dct_block[0][0])
        return dct_block

    @staticmethod
    def get_original_block_from_quantized(quantized_block: np.ndarray) -> np.ndarray:
        """
        Inverse of "getQuantizedBlock".
        :param quantized_block: Quantized 8x8 block of pixels [NUMPY NDARRAY]
        :return: Original 8x8 block of pixels [NUMPY NDARRAY]
        """
        dct_block = quantized_block
        dct_block[0][0] *= settings.QUANTIZATION_TABLE[0][0]
        unquantized_block = idct(dct_block)
        return np.add(unquantized_block, 128)

    # LENGTH EMBED/EXTRACT METHODS ====================================================

    def length_to_binary(self) -> list:
        """
        Gives binary form of the length and adds a separator to that representation.
        :return: Binary representation of the length + separator to embed [LIST OF STR]
        """
        if self.__message_length_ % 8 != 0:
            raise ValueError("Message length is not multiple of 8")
        msg_length = int(
            self.__message_length_ / 8
        )  # Decimal representation of the length
        n_required_bits = msg_length.bit_length()
        tmp = f"0{n_required_bits}b"
        binary_length = format(msg_length, tmp)
        return list(binary_length) + utils.string_to_binary(
            settings.LENGTH_MSG_SEPARATOR)

    def embed_msg_length(self):
        """
        Inserts the length of the message and end symbol (in binary form)
        at the beginning of the picture.
        At the end, '__block_list_' will be the image with embedded length,
        as list of blocks of pixels (from top left to bottom right) [LIST OF
                                                                    NUMPY NDARRAY]
        """
        mess_len_to_binary = self.length_to_binary()
        for block_index, length_bit_to_embed in enumerate(mess_len_to_binary):
            quantized_block = self.quantize_block(
                self.__block_list_[block_index])
            if quantized_block[0][0] % 2 == 1 and int(length_bit_to_embed) == 0:
                quantized_block[0][0] -= 1
            elif quantized_block[0][0] % 2 == 0 and int(
                    length_bit_to_embed) == 1:
                quantized_block[0][0] += 1
            self.__block_list_[
                block_index] = self.get_original_block_from_quantized(
                quantized_block)

    @staticmethod
    def extract_msg_length(img: np.ndarray) -> int:
        """
        Extracts the length (in bits) of the message embedded in the stegoimage.
        :param img: Stegoimage from which to extract the message [NUMPY NDARRAY]
        :return: Length of the message to extract from the stegoimage [INT]
        """
        block_index = 0
        separator_found = False
        decoded_length = ""
        while (not separator_found) and (
                block_index < settings.MAX_BITS_TO_ENCODE_LENGTH):
            block = utils.extract_block_from_image(img, block_index)
            unquantized_block = DCT.quantize_block(block)
            decoded_length += str(int(unquantized_block[0][0] % 2))
            if len(decoded_length) > 8:
                current_letter = str(chr(int(decoded_length[-8:], 2)))
                if current_letter == settings.LENGTH_MSG_SEPARATOR:
                    separator_found = True
            block_index += 1
        return int(''.join(decoded_length[:-8]), 2) * 8

    @staticmethod
    def get_random_blocks_from_msg_length(seed: int,
                                          binary_msg_length: int,
                                          height: int,
                                          width: int) -> list:
        """
        Generates a random sequence of indices, (interpreted as the position
        of bits of the message to embed/extract in/from the cover/stegoimage.
        :param seed: Chosen seed [INT]
        :param binary_msg_length: length of the message to extract
                                  from the stegoimage [INT]
        :param height: Height of the cover/stegoimage [INT]
        :param width: Width of the cover/stegoimage [INT]
        :return: List of indexes [LIST OF INT]
        """
        tot_blocks = height * width // 64
        random.seed(seed)
        chosen_blocks_indices = random.sample(
            range(settings.MAX_BITS_TO_ENCODE_LENGTH, tot_blocks),
            binary_msg_length)
        return chosen_blocks_indices

    def embed_msg(self, output_path: str, seed: int) -> np.ndarray:
        """
        Embed message into cover image:
        1 - Embed the length.
        2 - Embed the message equally distributing bits according
            to a random sequence of indices
            and inserting them in the LSB of DCT quantized blocks.
        :param output_path: Path of stegoimage that will be generated
                            after message insertion [STR]
        :param seed: Chosen seed [INT]
        :return: Stegoimage [NUMPY NDARRAY]
        """
        y, cr, cb = utils.get_YCrCb_from_original_img(self.__cover_image_)
        mess_len = len(self.__cipher_text_)
        positions_lst = self.get_random_blocks_from_msg_length(seed, mess_len * 8,
                                                               self.__height_,
                                                               self.__width_)
        self.__block_list_ = self.break_image_into_blocks(cb)
        self.embed_msg_length()
        for message_index, block_index in enumerate(positions_lst):
            block = self.__block_list_[block_index]
            dct_block = self.quantize_block(block)
            coeff = int(dct_block[0][0])

            message_bit = self.__bin_message_[message_index]
            if (coeff % 2) == 1 and int(message_bit) == 0:
                dct_block[0][0] -= 1
            elif (coeff % 2) == 0 and int(message_bit) == 1:
                dct_block[0][0] += 1

            self.__block_list_[block_index] = self.get_original_block_from_quantized(
                dct_block
            )
        modified_cb = self.recompose_image()
        final_img_standard_format = utils.get_original_img_from_YCrCb(y,
                                                                      cr,
                                                                      modified_cb)
        imwrite(output_path, final_img_standard_format)
        return final_img_standard_format

    @staticmethod
    def extract_msg(stego_img_path: str, seed: int) -> bytes:
        """
        Extract a message from a stegoimage:
        1 - Extract the length of the message.
        2 - Generate the random sequence of indices.
        3 - Extract the message.
        :param stego_img_path: Path of stegoimage
                               from which to extract the message [STR]
        :param seed: Chosen seed [INT]
        :return: Message hidden in the stegoimage [BYTE STR]
        """
        original_stego_img = utils.get_image(stego_img_path)
        _, _, cb = utils.get_YCrCb_from_original_img(original_stego_img)
        height, width = original_stego_img.shape[:2]
        msg_length = DCT.extract_msg_length(cb)
        positions_lst = DCT.get_random_blocks_from_msg_length(
            seed, msg_length, height, width)
        decoded_msg = "0b"
        block_list = DCT.break_image_into_blocks(cb)
        for message_index, block_index in enumerate(positions_lst):
            block_index = positions_lst[message_index]
            block = block_list[block_index]
            dct_block = DCT.quantize_block(block)
            coeff = int(dct_block[0][0])
            decoded_msg += str(
                coeff % 2)  # Adding to the message the currently read bit
        return BitArray(decoded_msg).bytes

class CoverImageBuilder:
    def __init__(self, image_path: str):
        self.__image_path_ = abspath(image_path)
        self.__output_path_ = self.gen_output_path(self.__image_path_)
        self.__original_pic_ = imageio.imread(self.__image_path_)
        self.__augmentor_ = ImageAugmentor(self.__original_pic_)
        self.__img_ = self.__original_pic_

    def get_output_path(self):
        return self.__output_path_

    @staticmethod
    def remove_exifs(image_path: str) -> str:
        """
        Remove EXIFS from an image.
        :param image_path: Path of the image from which need to remove EXIFS [STR]
        :return:
        """
        if image_path is None:
            raise TypeError
        output = subprocess.run(['exiftool', '-all=', image_path],
                                stdout=subprocess.PIPE,
                                stderr=subprocess.STDOUT,
                                shell=False)
        if output.stderr is not None:
            raise OSError
        return output.stdout.decode('utf-8')

    @staticmethod
    def gen_output_path(image_path: str) -> str:
        """
        Builds the output path of the final image.
        :param image_path: Original image path [STR]
        :return: Modified path [STR]
        """
        if image_path is None:
            raise TypeError
        index_last_point = image_path.rindex('.')
        return image_path[:index_last_point] + "_edited.png"

    def build_cover_image(self):
        """
        Builds the cover image:
        1) Performs augmentation
        2) Remove exifs
        """
        # augmented_img = self.__augmentor_.get_augmented_image()
        imageio.imwrite(self.__output_path_, self.__original_pic_)
        self.remove_exifs(self.__output_path_)

from base64 import urlsafe_b64encode
from os import path, remove, urandom
from zlib import compress, decompress

from cryptography.fernet import Fernet, InvalidToken
from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC

from settings import SALT_LEN, DK_LEN, COUNT, COULD_NOT_DECRYPT


def gen_salted_key_from_password(salt: bytes, password: str) -> bytes:
    """
    Generates the salted key given a password
    :param salt: Random generated salt [BYTE STR]
    :param password: Password from which key will be derived [STR]
    :return: Password derived key [STR]
    """
    kdf = PBKDF2HMAC(
        algorithm=hashes.SHA256(),
        length=DK_LEN,
        salt=salt,
        iterations=COUNT,
        backend=default_backend()
    )
    key = urlsafe_b64encode(kdf.derive(password.encode()))
    return key


def encrypt_message(message_to_encrypt: str, password: str) -> bytes:
    """
    Encrypts a message given a password.
    :param message_to_encrypt: Message to encrypt [STR]
    :param password: Password from which key will be derived [STR]
    :return: Salt concatenated to the cipher message [STR]
    """
    encoded_to_encrypt = message_to_encrypt.encode('utf-8')
    compressed_to_encrypt = compress(encoded_to_encrypt)
    salt = urandom(SALT_LEN)
    key = gen_salted_key_from_password(salt, password)
    cipher = Fernet(key).encrypt(compressed_to_encrypt)
    return salt + cipher


def decrypt_message(cipher_message: bytes, password: str):
    """
    Decrypts a cipher given the password.
    :param cipher_message: Salt concatenated to the cipher message [STR]
    :param password: Password from which key will be derived [STR]
    :return: Decrypted message [STR]
    or settings.COULD_NOT_DECRYPT if could not decrypt
    """
    key = gen_salted_key_from_password(salt=cipher_message[:SALT_LEN],
                                       password=password)
    try:
        pt = Fernet(key).decrypt(cipher_message[SALT_LEN:])
        original_message = decompress(pt).decode('utf-8')
    except InvalidToken:
        return COULD_NOT_DECRYPT
    return original_message

import imgaug as ia
import imgaug.augmenters as iaa

import settings as st

def sometimes(aug: iaa):
    """
    Sometimes(0.5, ...) applies the given augmenter in 50% of all cases,
    e.g. Sometimes(0.5, GaussianBlur(0.3)) would blur roughly every second image.
    :param aug: Type of augmentation
    :return: Desired augmentation with a certain probability
    """
    return iaa.Sometimes(0.8, aug)


class ImageAugmentor:
    def __init__(self, img: ia.imageio.core.util.Array):
        self.__original_pic_ = img
        self.__augmented_pic_ = None
        self.__seq_ = iaa.Sequential(
            [
                iaa.Fliplr(st.P_HORIZONTAL_FLIP),
                iaa.Flipud(st.P_VERTICAL_FLIP),  # vertically flip
                # crop images
                sometimes(iaa.CropAndPad(
                    percent=(st.MIN_CROP, st.MAX_CROP),
                    pad_mode=ia.ALL,
                    pad_cval=(0, 255)
                )),
                sometimes(iaa.Affine(
                    # scale images
                    scale={"x": (st.MIN_SCALE, st.MAX_SCALE),
                           "y": (st.MIN_SCALE, st.MAX_SCALE)},
                    # translate
                    translate_percent={
                        "x": (st.MIN_TRANSLATE, st.MAX_TRANSLATE),
                        "y": (st.MIN_TRANSLATE, st.MAX_TRANSLATE)},
                    rotate=(st.MIN_ROTATION, st.MAX_ROTATION),  # rotate
                    shear=(st.MIN_SHEAR, st.MAX_SHEAR),  # shear
                    order=[0, 1],
                    # use nearest neighbour or bilinear interpolation (fast)
                    cval=(0, 255),
                    # if mode is constant, use a cval between 0 and 255
                    mode=ia.ALL
                    # use any of scikit-image's warping modes
                    # (see 2nd image from the top for examples)
                )),
                # execute 0 to 5 of the following (less important) augmenters per image
                # don't execute all of them, as that would often be way too strong
                iaa.SomeOf((0, 5),
                           [
                               # convert images into their superpixel representation
                               sometimes(
                                   iaa.Superpixels(p_replace=(
                                       st.MIN_P_REPLACE_SUPERPIXEL,
                                       st.MAX_P_REPLACE_SUPERPIXEL),
                                       n_segments=(
                                           st.MIN_SUPERPIXELS_PER_IMAGE,
                                           st.MAX_SUPERPIXELS_PER_IMAGE))),
                               iaa.OneOf([
                                   iaa.GaussianBlur(
                                       (st.MIN_BLUR_SIGMA, st.MAX_BLUR_SIGMA)),
                                   # blur images
                                   iaa.AverageBlur(k=(st.MIN_LOCAL_BLUR_SIZE,
                                                      st.MAX_LOCAL_BLUR_SIZE)),
                                   # blur image using local means
                                   # with kernel sizes between 2 and 7
                                   iaa.MedianBlur(k=(3, 11)),
                               ]),
                               iaa.Sharpen(alpha=(
                                   st.MIN_SHARPEN_ALPHA, st.MAX_SHARPEN_ALPHA),
                                   lightness=(0.75, 1.5)),
                               # sharpen images
                               iaa.Emboss(alpha=(
                                   st.MIN_EMBOSS_ALPHA, st.MAX_EMBOSS_ALPHA),
                                   strength=(0, 2.0)),
                               # emboss images
                               # search either for all edges or for directed edges,
                               # blend the result with the original image
                               # using a blobby mask
                               iaa.SimplexNoiseAlpha(iaa.OneOf([
                                   iaa.EdgeDetect(alpha=(
                                       st.MIN_EDGE_DETECTION_ALPHA,
                                       st.MAX_EDGE_DETECTION_ALPHA)),
                                   iaa.DirectedEdgeDetect(alpha=(0.5, 1.0),
                                                          direction=(0.0, 1.0)),
                               ])),
                               iaa.AdditiveGaussianNoise(loc=0, scale=(
                                   0.0, 0.05 * 255), per_channel=0.5),
                               # add gaussian noise to images
                               iaa.OneOf([
                                   iaa.Dropout((st.MIN_DROPOUT, st.MAX_DROPOUT),
                                               per_channel=0.5),
                                   # randomly remove pixels
                                   iaa.CoarseDropout((st.MIN_COARSE_DROPOUT,
                                                      st.MAX_COARSE_DROPOUT),
                                                     size_percent=(0.02, 0.05),
                                                     per_channel=0.2),
                               ]),
                               iaa.Invert(st.P_INVERSION, per_channel=True),
                               # invert color channels
                               iaa.Add((st.MIN_BRIGHTNESS_PURC,
                                        st.MAX_BRIGHTNESS_PURC),
                                       per_channel=0.5),
                               # change brightness of image
                               iaa.AddToHueAndSaturation((st.MIN_HUE_SATURATION,
                                                          st.MAX_HUE_SATURATION)),
                               # change hue and saturation
                               # either change the brightness of the whole image
                               # (sometimes per channel)
                               # or change the brightness of subareas
                               iaa.OneOf([
                                   iaa.Multiply((0.5, 1.5), per_channel=0.5),
                                   iaa.FrequencyNoiseAlpha(
                                       exponent=(-4, 0),
                                       first=iaa.Multiply((0.5, 1.5),
                                                          per_channel=True),
                                       second=iaa.LinearContrast((0.5, 2.0))
                                   )
                               ]),
                               # improve or worsen the contrast
                               iaa.LinearContrast(
                                   (st.MIN_CONTRAST, st.MAX_CONTRAST),
                                   per_channel=0.5),
                               iaa.Grayscale(alpha=(0.0, 1.0)),
                               sometimes(
                                   iaa.ElasticTransformation(alpha=(0.5, 3.5),
                                                             sigma=0.25)),
                               # move pixels locally around (with random strengths)
                               sometimes(iaa.PiecewiseAffine(scale=(
                                   st.MIN_PIECEWISE_SCALE,
                                   st.MAX_PIECEWISE_SCALE))),
                               # sometimes move parts of the image around
                               sometimes(iaa.PerspectiveTransform(
                                   scale=(st.MIN_PERSP_TRANSF_SCALE,
                                          st.MAX_PERSP_TRANSF_SCALE)))
                           ],
                           random_order=True
                           )
            ],
            random_order=True
        )

    def get_augmented_image(self):
        self.__augmented_pic_ = self.__seq_.augment_image(self.__original_pic_)
        return self.__augmented_pic_




def embed(original_image_path: str,
          stego_image_output_path: str,
          message: str,
          password: str,
          chosen_seed: int):
    """
    :param original_image_path: Original image path [STR]
    :param stego_image_output_path: Path of the output stegoimage [STR]
    :param message: Message to hide into the stegoimage [STR]
    :param password: Password to encrypt the message [STR]
    :param chosen_seed: A seed for the uniform bits distribution in the image [INT]
    :return: Path to the cover image
    """
    absolute_original_image_path = path.realpath(original_image_path)
    absolute_output_path = path.realpath(stego_image_output_path)
    cib = CoverImageBuilder(absolute_original_image_path)
    cib.build_cover_image()
    cover_image_path = cib.get_output_path()
    encrypted_message = encrypt_message(message, password)
    embedder = DCT(cover_image_path, encrypted_message)
    embedder.embed_msg(absolute_output_path, chosen_seed)
    return cover_image_path


def extract(stego_img_path: str, password: str, chosen_seed: int):
    """
    Extract the hidden message from the stegoimage.
    :param stego_img_path: Path to the stego image [STR]
    :param password: Password the message was encrypted with [STR]
    :param chosen_seed: Chosen seed [INT]
    :return: Extracted and decrypted message [STR] (or error code)
    """
    absolute_stegoimage_path = path.realpath(stego_img_path)
    extracted_encrypted_message = DCT.extract_msg(absolute_stegoimage_path,
                                                  chosen_seed)
    decrypted_message = decrypt_message(extracted_encrypted_message, password)
    return decrypted_message

from PIL import Image


class Steganography:

    BLACK_PIXEL = (0, 0, 0)

    def _int_to_bin(self, rgb):
        """Convert an integer tuple to a binary (string) tuple.
        :param rgb: An integer tuple like (220, 110, 96)
        :return: A string tuple like ("00101010", "11101011", "00010110")
        """
        r, g, b = rgb
        return f'{r:08b}', f'{g:08b}', f'{b:08b}'

    def _bin_to_int(self, rgb):
        """Convert a binary (string) tuple to an integer tuple.
        :param rgb: A string tuple like ("00101010", "11101011", "00010110")
        :return: Return an int tuple like (220, 110, 96)
        """
        r, g, b = rgb
        return int(r, 2), int(g, 2), int(b, 2)

    def _merge_rgb(self, rgb1, rgb2):
        """Merge two RGB tuples.
        :param rgb1: An integer tuple like (220, 110, 96)
        :param rgb2: An integer tuple like (240, 95, 105)
        :return: An integer tuple with the two RGB values merged.
        """
        r1, g1, b1 = self._int_to_bin(rgb1)
        r2, g2, b2 = self._int_to_bin(rgb2)
        rgb = r1[:4] + r2[:4], g1[:4] + g2[:4], b1[:4] + b2[:4]
        return self._bin_to_int(rgb)

    def _unmerge_rgb(self, rgb):
        """Unmerge RGB.
        :param rgb: An integer tuple like (220, 110, 96)
        :return: An integer tuple with the two RGB values merged.
        """
        r, g, b = self._int_to_bin(rgb)
        # Extract the last 4 bits (corresponding to the hidden image)
        # Concatenate 4 zero bits because we are working with 8 bit
        new_rgb = r[4:] + '0000', g[4:] + '0000', b[4:] + '0000'
        return self._bin_to_int(new_rgb)

    def merge(self, image1, image2):
        """Merge image2 into image1.
        :param image1: First image
        :param image2: Second image
        :return: A new merged image.
        """
        # Check the images dimensions
        if image2.size[0] > image1.size[0] or image2.size[1] > image1.size[1]:
            raise ValueError('Image 2 should be smaller than Image 1!')

        # Get the pixel map of the two images
        map1 = image1.load()
        map2 = image2.load()

        new_image = Image.new(image1.mode, image1.size)
        new_map = new_image.load()

        for i in range(image1.size[0]):
            for j in range(image1.size[1]):
                is_valid = lambda: i < image2.size[0] and j < image2.size[1]
                rgb1 = map1[i ,j]
                rgb2 = map2[i, j] if is_valid() else self.BLACK_PIXEL
                new_map[i, j] = self._merge_rgb(rgb1, rgb2)

        return new_image

    def unmerge(self, image):
        """Unmerge an image.
        :param image: The input image.
        :return: The unmerged/extracted image.
        """
        pixel_map = image.load()

        # Create the new image and load the pixel map
        new_image = Image.new(image.mode, image.size)
        new_map = new_image.load()

        for i in range(image.size[0]):
            for j in range(image.size[1]):
                new_map[i, j] = self._unmerge_rgb(pixel_map[i, j])

        return new_image
    
long_paragraph = """Lorem ipsum dolor sit amet, consectetur adipiscing elit.
                    Donec a diam lectus. Sed sit amet ipsum mauris. Maecenas
                    congue ligula ac quam viverra nec consectetur ante
                    hendrerit. Donec et mollis dolor. Praesent et diam eget
                    libero egestas mattis sit amet vitae augue. Nam tincidunt
                    congue enim, ut porta lorem lacinia consectetur. Donec ut
                    libero sed arcu vehicula ultricies a non tortor. Lorem
                    ipsum dolor sit amet, consectetur adipiscing elit. Aenean
                    ut gravida lorem. Ut turpis felis, pulvinar a semper sed,
                    adipiscing id dolor. Pellentesque auctor nisi id magna
                    consequat sagittis. Curabitur dapibus enim sit amet elit
                    pharetra tincidunt feugiat nisl imperdiet. Ut convallis
                    libero in urna ultrices accumsan. Donec sed odio eros.
                    """

def run_embed():
    files = glob.glob("test_images/*.jpg")
    for file in files:
        filename = path.splitext(path.basename(file))[0]
        output_file = f"test_images/output/{filename}_stego.png"
        if path.exists(output_file):
            remove(output_file)
        print(f"Embedding the Message in {file} and saving it as {output_file}")
        embed(file, output_file, long_paragraph, "password", 42)
        

def run_extract():
    #find all the stego images in the output folder
    files = glob.glob("test_images/output/*_stego.png")
    for file in files:
        filename = path.splitext(path.basename(file))[0]
        print(f"Extracting the Message from {file}")
        print(extract(file, "password", 42))

if __name__ == '__main__':
    # remove the output file if it exists
    # if path.exists("test_images/lena_stego.png"):
    #     remove("test_images/lena_edited.png")
    #     remove("test_images/lena_stego.png")
    run_embed()  
    run_extract()  
    # l = embed("test_images/lena.jpg", "test_images/lena_stego.png", "Sidd ", "password", 42)
    # image1 = Image.open("test_images/lena.jpg")
    # image2 = Image.open("test_images/lena_stego.png")

    # if path.exists("test_images/lena_stego_merged.png"):
    #     remove("test_images/lena_stego_merged.png")
    # Steganography().merge(image1, image2).save("test_images/lena_stego_merged.png")
    # print("Extracting the Message")
    # image = Image.open("test_images/lena_stego_merged.png")
    # Steganography().unmerge(image).save("test_images/lena_stego_unmerged.png")
    # print(extract("test_images/lena_stego_unmerged.png", "password", 42))
