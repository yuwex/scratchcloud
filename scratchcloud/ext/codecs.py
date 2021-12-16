from textwrap import wrap
from ..errors import EncodeError, DecodeError

class BaseCodec:
    def __init__(self, alphabet: str = 'abcdefghijklmnopqrstuvwxyz1234567890 -=[]\\;\',./!@#$%^&*()_+{}|:\"<>?'):
        self.plainalpha = list(alphabet)
        
        cipher_ints = list(range(10, len(self.plainalpha) + 10))
        self.cipheralpha = [str(v) for v in cipher_ints]

    def encode(self, plaintext: str) -> str:
        try:
            encoded = []
            for letter in plaintext.lower():
                letter = self.cipheralpha[self.plainalpha.index(letter)]
                encoded.append(letter)
            return ''.join(encoded)
        except Exception as e:
            raise EncodeError(f'Unable to encode: {plaintext} due to \n{e}')

    def decode(self, ciphertext: str) -> str:
        try:
            decoded = []
            for letter in wrap(ciphertext.lower(), 2):
                letter = self.plainalpha[self.cipheralpha.index(letter)]
                decoded.append(letter)
            return ''.join(decoded)
        except Exception as e:
            raise DecodeError(f'Unable to decode: {ciphertext} due to \n{e}')

