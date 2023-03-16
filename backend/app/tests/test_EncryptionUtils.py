import random
import string
from unittest import TestCase

from eclipse.src.encryption_utils import encrypt_message, decrypt_message


def generate_random_string(string_length: int) -> str:
    """
    Util function to generate random message and password for tests.
    :param string_length: Length of the desired random string [INT]
    :return: Random string of length 'stringLength' [STR]
    """
    letters = string.ascii_letters + string.digits + string.punctuation
    return ''.join(random.choice(letters) for _ in range(string_length))


class Test(TestCase):

    def test_encrypt_message(self):
        for _ in range(40):
            message_to_encrypt = generate_random_string(random.randint(1, 1000))
            password = generate_random_string(random.randint(1, 40))
            res = encrypt_message(message_to_encrypt, password)
            self.assertEqual(message_to_encrypt, decrypt_message(res, password))
