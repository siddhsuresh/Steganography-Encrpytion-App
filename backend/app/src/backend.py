from __future__ import print_function, unicode_literals

from os import path
import eclipse.common.settings as error_codes
from eclipse.src.cover_image_builder import CoverImageBuilder
from eclipse.src.discrete_cosine_transform_tool import DCT
from eclipse.src.encryption_utils import encrypt_message, decrypt_message
from eclipse.common.utils import image_exists, is_a_good_place

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
    if not image_exists(absolute_original_image_path):
        return error_codes.ORIGINAL_IMAGE_PATH_DOES_NOT_EXISTS
    if not is_a_good_place(absolute_output_path):
        return error_codes.OUTPUT_IMAGE_PATH_DOES_NOT_EXISTS

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
    if not image_exists(absolute_stegoimage_path):
        return error_codes.ORIGINAL_IMAGE_PATH_DOES_NOT_EXISTS
    extracted_encrypted_message = DCT.extract_msg(absolute_stegoimage_path,
                                                  chosen_seed)
    decrypted_message = decrypt_message(extracted_encrypted_message, password)
    return decrypted_message
