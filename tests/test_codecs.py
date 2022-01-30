import unittest
from scratchcloud.ext import BaseCodec
from scratchcloud import errors

class TestBaseCodec(unittest.TestCase):

    def test_init(self):
        codec = BaseCodec('abc')
        self.assertEqual(codec.plainalpha, ['a', 'b', 'c'])
        self.assertEqual(codec.cipheralpha, ['10', '11', '12'])

        codec = BaseCodec('abc', offset=0)
        self.assertEqual(codec.plainalpha, ['a', 'b', 'c'])
        self.assertEqual(codec.cipheralpha, ['00', '01', '02'])

        codec = BaseCodec('abc', places_per_character=4)
        self.assertEqual(codec.plainalpha, ['a', 'b', 'c'])
        self.assertEqual(codec.cipheralpha, ['0010', '0011', '0012'])

        codec = BaseCodec('abc', offset=1000, places_per_character=4)
        self.assertEqual(codec.plainalpha, ['a', 'b', 'c'])
        self.assertEqual(codec.cipheralpha, ['1000', '1001', '1002'])

    def test_encode(self):
        codec = BaseCodec()
        self.assertEqual(codec.encode('hello'), '1714212124')
        self.assertRaises(errors.EncodeError, codec.encode, 'Hello')

        codec = BaseCodec(force_lowercase=True)
        self.assertEqual(codec.encode('HELLO'), '1714212124')

        codec = BaseCodec(places_per_character=4)
        self.assertEqual(codec.encode('hello'), '00170014002100210024')

        codec = BaseCodec(offset=1000, places_per_character=4)
        self.assertEqual(codec.encode('hello'), '10071004101110111014')

    def test_decode(self):
        codec = BaseCodec()
        self.assertEqual(codec.decode('1714212124'), 'hello')
        self.assertRaises(errors.DecodeError, codec.decode, '400')

        codec = BaseCodec('ABC', force_lowercase=True)
        self.assertEqual(codec.decode('101112'), 'abc')

        codec = BaseCodec(places_per_character=4)
        self.assertEqual(codec.decode('00170014002100210024'), 'hello')

        codec = BaseCodec(offset=1000, places_per_character=4)
        self.assertEqual(codec.decode('10071004101110111014'), 'hello')

if __name__ == '__main__':
    unittest.main()