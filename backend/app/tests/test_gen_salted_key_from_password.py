from unittest import TestCase

from eclipse.src.encryption_utils import gen_salted_key_from_password


class Test(TestCase):
    def test_gen_salted_key_from_password(self):
        salts = [
            b'\xc1\xfd\xec\xcf\x7f\x83\xb9\xcc\xdc\xa4\xf9\xf7\xd3\xcd\x98W\xfb|'
            b'\x969\xae\xd9\x8e\xbd\xed\xb4\xbd;\x88Pe\x13',
            b'\xac\xf9o#\xa0&3\xa7S\x15\x08\x97/\xef3\xe7F\xfd\x19'
            b'\xbd\xfcu&5\xee"\xddP\x82\xb5"\xa2',
            b'\x1d\x9bg\xa9\xcdg\xac\x81`sc?\xaf\x04\x81\xbb\xa1\xa5'
            b'\x92\x92\x15\x8e\xa0h\nQ\x94\xb5\x0c\xd6d\xdf',
            b'\xb9q\xda\x85\x08\x1c\xa8\xd8\xe4\x10a\xbb\xcaW\xbbH'
            b'\x1bQ\x92-\xa1\x0c\xcd\xf4\xb4\xba"\xcd\xdc\x162\n',
            b"\x0b\xb7\x9f\xda\xea\\\xb4j\xde\xf2\x86d\x92\xe08b"
            b"\xae\x8c\x8d\x1f\xaeA'ne1>\xb1|x\x99Y",
            b'"\xd1\x93\xa8\xd3\x9d\xed\xcb\xaa\xd1\x19\xc7{\x10'
            b'\xef\x95\xef\x7f\xd8\xd1\x90\xe6\x1c\xae\xbf?\xadO\xa4|c\xe4',
            b'\x11\xd4$\x8b\xec\x01\xfb\xa9\x1d\xfak\xc3L\xd4\x88'
            b'\xfeR>\xb90\xc1vxA\xaf\xf9\x83\x8b\xcd\xc4\xffy',
            b'\xb9\x0c\x01\xd6\x14\xc8"\xb54\x13\xd9\xb2\xc2'
            b'\xc9x{\xf4\xd4pRI+\xc9\'3&$^\x9a\x0eo\xff',
            b'\xd6u\xd4]\xca\x1d\xa9\xf6n\x9du\xc2\x14\xd5\xcetu'
            b'\x1c\xed\xfa\xe7\x1f\t\xea\x89\x8b6|\xbd!7\xc4',
            b'\xd1\xe7\x035z\xe4\x93\xa7T\x95RM\xaf\xccn\x9aR,'
            b'\x1b\xb9\xf4\xe9?\x0b-\x8bF\xe9\xc8lu\xb2']
        keys = [b'ic6viKdFUOiiIA-h8wo6Z0S2p9nPbjbllc69oMClVQ0=',
                b'8CPW8WUL6Fb3TG4kNl33_2R9Yk8PxzoBDkb7YSDknf0=',
                b'DHVx0-_oPPUzXwcw563WjAdXTHuntalmmLC7xqNdjsc=',
                b'eabdnxKd668lpm2NLqp4EFSCH3Pfh7G3s6jHvpxJMGo=',
                b'6FtvbHiMKdWseADH3aE1IviKymAKKPX9M729HMhVgss=',
                b'QnrOs-WcsVO1XVHmvXuOeWv_6K9fuOsYFRklSZlULgY=',
                b'5O_veVNglUmNjIx_pGf1Kv3lnMM3CvFuwiKe9AtJGiY=',
                b'ZRrNIx_oRJWdafckdaikzfCcXYEBaPuYkyxx2F8WyIg=',
                b'jCoUNvEY9TaiLe6ArXLJV5pQnBc-rdBbMqBueZ-7s0A=',
                b'L7yBFZSFfpQatB-SH_PNFe5bIOaG0QTSWfn5OIRIVks=']

        for i, salt in enumerate(salts):
            self.assertEqual(
                gen_salted_key_from_password(salt, "pass"),
                keys[i]
            )
