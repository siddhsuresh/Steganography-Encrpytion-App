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

    def verify_ciphertext_size(self):
        area = self.__height_ * self.__width_
        if area < 64:  # 64 -> since each quantized block is a matrix of 8x8
            raise ValueError("The chosen cover image is too small (area < 64 px)")
        tot_blocks = self.__height_ * self.__width_ // 64
        if self.__message_length_ > tot_blocks:
            raise OverflowError("Cannot embed. Message is too long!")
        if self.__message_length_ > tot_blocks / 10:
            purcentage_of_occupied_storage = round(
                self.__message_length_ / tot_blocks * 100
            )
            warning = (
                f"Message occupies ≈ "
                f"{purcentage_of_occupied_storage}% of the pic. "
                "A smaller text is preferred (< 10%)"
            )
            warn(warning)

    def verify_and_apply_padding(self):
        original_height, original_width = self.__cover_image_.shape[:2]
        if original_height % 8 != 0 or original_width % 8 != 0:
            self.__cover_image_ = resize(
                self.__cover_image_,
                (
                    original_width + (8 - original_width % 8),
                    original_height + (8 - original_height % 8),
                ),
            )
            imwrite(self.__cover_image_path_, self.__cover_image_)

    @staticmethod
    def break_image_into_blocks(img: np.ndarray) -> list:
        if not isinstance(img, np.ndarray):
            raise TypeError("Cannot break a non np.array image")
        height, width = len(img), len(img[0])
        return [
            img[j : j + 8, i : i + 8]
            for (j, i) in product(range(0, height, 8), range(0, width, 8))
        ]

    def recompose_image(self) -> np.ndarray:
        if len(self.__block_list_) == 0:
            raise ValueError
        full_image = np.zeros(
            shape=(self.__height_, self.__width_), dtype=np.uint8
        )  # Builds empty image
        for i in range(len(self.__block_list_)):  # Filling image
            curr_col_index = 8 * (i % (self.__width_ // 8))
            curr_line_index = 8 * (i // (self.__width_ // 8))
            full_image[
                curr_line_index : curr_line_index + 8,
                curr_col_index : curr_col_index + 8,
            ] = self.__block_list_[i]
        return full_image

    @staticmethod
    def quantize_block(block: np.ndarray) -> np.ndarray:
        img_block = np.subtract(block, 128)
        dct_block = dct(img_block.astype(np.float64))
        dct_block[0][0] /= settings.QUANTIZATION_TABLE[0][0]
        dct_block[0][0] = np.round(dct_block[0][0])
        return dct_block

    @staticmethod
    def get_original_block_from_quantized(quantized_block: np.ndarray) -> np.ndarray:
        dct_block = quantized_block
        dct_block[0][0] *= settings.QUANTIZATION_TABLE[0][0]
        unquantized_block = idct(dct_block)
        return np.add(unquantized_block, 128)

    def length_to_binary(self) -> list:
        if self.__message_length_ % 8 != 0:
            raise ValueError("Message length is not multiple of 8")
        msg_length = int(
            self.__message_length_ / 8
        )  # Decimal representation of the length
        n_required_bits = msg_length.bit_length()
        tmp = f"0{n_required_bits}b"
        binary_length = format(msg_length, tmp)
        return list(binary_length) + utils.string_to_binary(
            settings.LENGTH_MSG_SEPARATOR
        )

    def embed_msg_length(self):
        mess_len_to_binary = self.length_to_binary()
        for block_index, length_bit_to_embed in enumerate(mess_len_to_binary):
            quantized_block = self.quantize_block(self.__block_list_[block_index])
            if quantized_block[0][0] % 2 == 1 and int(length_bit_to_embed) == 0:
                quantized_block[0][0] -= 1
            elif quantized_block[0][0] % 2 == 0 and int(length_bit_to_embed) == 1:
                quantized_block[0][0] += 1
            self.__block_list_[block_index] = self.get_original_block_from_quantized(
                quantized_block
            )

    @staticmethod
    def extract_msg_length(img: np.ndarray) -> int:
        block_index = 0
        separator_found = False
        decoded_length = ""
        while (not separator_found) and (
            block_index < settings.MAX_BITS_TO_ENCODE_LENGTH
        ):
            block = utils.extract_block_from_image(img, block_index)
            unquantized_block = DCT.quantize_block(block)
            decoded_length += str(int(unquantized_block[0][0] % 2))
            if len(decoded_length) > 8:
                current_letter = str(chr(int(decoded_length[-8:], 2)))
                if current_letter == settings.LENGTH_MSG_SEPARATOR:
                    separator_found = True
            block_index += 1
        return int("".join(decoded_length[:-8]), 2) * 8

    @staticmethod
    def get_random_blocks_from_msg_length(
        seed: int, binary_msg_length: int, height: int, width: int
    ) -> list:
        tot_blocks = height * width // 64
        random.seed(seed)
        chosen_blocks_indices = random.sample(
            range(settings.MAX_BITS_TO_ENCODE_LENGTH, tot_blocks), binary_msg_length
        )
        return chosen_blocks_indices

    def embed_msg(self, output_path: str, seed: int) -> np.ndarray:
        y, cr, cb = utils.get_YCrCb_from_original_img(self.__cover_image_)
        mess_len = len(self.__cipher_text_)
        positions_lst = self.get_random_blocks_from_msg_length(
            seed, mess_len * 8, self.__height_, self.__width_
        )
        # print(positions_lst)
        self.__block_list_ = self.break_image_into_blocks(cb)
        self.embed_msg_length()
        for message_index, block_index in enumerate(positions_lst):
            block = self.__block_list_[block_index]
            dct_block = self.quantize_block(block)
            # print(dct_block)
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
        final_img_standard_format = utils.get_original_img_from_YCrCb(
            y, cr, modified_cb
        )
        imwrite(output_path, final_img_standard_format)
        return final_img_standard_format

    @staticmethod
    def extract_msg(stego_img_path: str, seed: int) -> bytes:
        original_stego_img = utils.get_image(stego_img_path)
        _, _, cb = utils.get_YCrCb_from_original_img(original_stego_img)
        height, width = original_stego_img.shape[:2]
        msg_length = DCT.extract_msg_length(cb)
        positions_lst = DCT.get_random_blocks_from_msg_length(
            seed, msg_length, height, width
        )
        decoded_msg = "0b"
        block_list = DCT.break_image_into_blocks(cb)
        for message_index, block_index in enumerate(positions_lst):
            block_index = positions_lst[message_index]
            block = block_list[block_index]
            dct_block = DCT.quantize_block(block)
            coeff = int(dct_block[0][0])
            decoded_msg += str(
                coeff % 2
            )  # Adding to the message the currently read bit
        return BitArray(decoded_msg).bytes


class CoverImageBuilder:
    def __init__(self, image_path: str):
        self.__image_path_ = abspath(image_path)
        self.__output_path_ = self.gen_output_path(self.__image_path_)
        self.__original_pic_ = imageio.imread(self.__image_path_)

    def get_output_path(self):
        return self.__output_path_

    @staticmethod
    def remove_exifs(image_path: str) -> str:
        if image_path is None:
            raise TypeError
        output = subprocess.run(
            ["exiftool", "-all=", image_path],
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            shell=False,
        )
        if output.stderr is not None:
            raise OSError
        return output.stdout.decode("utf-8")

    @staticmethod
    def gen_output_path(image_path: str) -> str:
        if image_path is None:
            raise TypeError
        index_last_point = image_path.rindex(".")
        return image_path[:index_last_point] + "_edited.png"

    def build_cover_image(self):
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
    kdf = PBKDF2HMAC(
        algorithm=hashes.SHA256(),
        length=DK_LEN,
        salt=salt,
        iterations=COUNT,
        backend=default_backend(),
    )
    key = urlsafe_b64encode(kdf.derive(password.encode()))
    return key


def encrypt_message(message_to_encrypt: str, password: str) -> bytes:
    encoded_to_encrypt = message_to_encrypt.encode("utf-8")
    compressed_to_encrypt = compress(encoded_to_encrypt)
    salt = urandom(SALT_LEN)
    key = gen_salted_key_from_password(salt, password)
    cipher = Fernet(key).encrypt(compressed_to_encrypt)
    return salt + cipher


def decrypt_message(cipher_message: bytes, password: str):
    key = gen_salted_key_from_password(
        salt=cipher_message[:SALT_LEN], password=password
    )
    try:
        pt = Fernet(key).decrypt(cipher_message[SALT_LEN:])
        original_message = decompress(pt).decode("utf-8")
    except InvalidToken:
        return COULD_NOT_DECRYPT
    return original_message


def embed(
    original_image_path: str,
    stego_image_output_path: str,
    message: str,
    password: str,
    chosen_seed: int,
):
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
    absolute_stegoimage_path = path.realpath(stego_img_path)
    extracted_encrypted_message = DCT.extract_msg(absolute_stegoimage_path, chosen_seed)
    decrypted_message = decrypt_message(extracted_encrypted_message, password)
    return decrypted_message


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

# import glob
# from os import path, remove
# import random
# import string

# def run_embed(text, password):
#     files = glob.glob("src/test_images/*.jpg",root_dir="/home/siddharth/Projects/Crypto/backend/")
#     print(files)
#     for file in files:
#         text = ''.join(random.choice(string.ascii_uppercase + string.digits) for _ in range(100))
#         filename = path.splitext(path.basename(file))[0]
#         output_file = f"src/test_images/output/{filename}_stego.png"
#         if path.exists(output_file):
#             remove(output_file)
#         print(f"Embedding the Message in {file} and saving it as {output_file}")
#         embed(file, output_file, text , password, 42)
#         print("Encoded Message: " + text)


# def run_extract():
#     files = glob.glob("src/test_images/output/*_stego.png",root_dir="/home/siddharth/Projects/Crypto/backend/")
#     for file in files:
#         filename = path.splitext(path.basename(file))[0]
#         print(f"Extracting the Message from {file}")
#         print("Encoded message in cover image {} is -> {} " .format(filename, extract(file, "password", 42)))

# import sys

# if __name__ == '__main__':
#     text,password = sys.argv[1],sys.argv[2]
#     run_embed(text,password)
#     run_extract()

import hashlib
import rsa
import base64

from cs50 import SQL

db = SQL("sqlite:////home/siddharth/Projects/Crypto/backend/src/database.db")

# create a table which has the base64 encoded public key, sha256 hash of the original image and the stego image
db.execute(
    "CREATE TABLE IF NOT EXISTS stego (original_image TEXT, stego_image TEXT)"
)

with open("/home/siddharth/Projects/Crypto/backend/src/public.pem", "rb") as publicfile:
    p = publicfile.read()
    pubkey = rsa.PublicKey.load_pkcs1(p)

with open("/home/siddharth/Projects/Crypto/backend/src/private.pem", "rb") as privatefile:
    p = privatefile.read()
    privkey = rsa.PrivateKey.load_pkcs1(p)

def sign(message):
    signature = rsa.sign(message, privkey, "SHA-1")
    signature = signature.hex()
    return signature


def verify(message, signature):
    try:
        rsa.verify(message, signature, pubkey)
        return True
    except:
        return False


def encrypt(message):
    crypto = rsa.encrypt(message.encode(), pubkey)
    return crypto


def decrypt(crypto):
    message = rsa.decrypt(crypto, privkey)
    return message


import sys

def main():
    if sys.argv[1] == "-e":
        image_path = sys.argv[2]
        output_path = sys.argv[3]
        message = sys.argv[4]
        password = sys.argv[5]
        embed(image_path, output_path, message, password, 42)
        with open(image_path, "rb") as image_file:
            encoded_string = base64.b64encode(image_file.read())
        with open(output_path, "rb") as image_file:
            encoded_string2 = base64.b64encode(image_file.read())
        og_signature = sign(encoded_string)
        stego_signature = sign(encoded_string2)
        if db.execute("SELECT * FROM stego WHERE original_image = ?", og_signature):
            db.execute(
                "UPDATE stego SET stego_image = ? WHERE original_image = ?",
                stego_signature,
                og_signature,
            )
        else:
            db.execute(
                "INSERT INTO stego (original_image, stego_image) VALUES (?, ?)",
                og_signature,
                stego_signature,
            )
        # print("Message Encoded Successfully")
        print(str(og_signature))
        # print("Stego Image Signature: " + str(stego_signature))
        
    elif sys.argv[1] == "-d":
        output_path = sys.argv[2]
        password = sys.argv[3]
        og_image_sign = sys.argv[4]
        stego_image_sign = db.execute("SELECT stego_image FROM stego WHERE original_image = ?", og_image_sign)
        stego_image_sign = stego_image_sign[0]["stego_image"]
        with open(output_path, "rb") as image_file:
            encoded_string = base64.b64encode(image_file.read())
        _stego_signature = sign(encoded_string)
        if _stego_signature == stego_image_sign:
            # print("Image is Authentic")
            message = extract(output_path, password, 42)
            print(str(message))
        else:
            print("Image has been tampered with")
    else:
        print("Invalid Argument")


if __name__ == "__main__":
    main()
