
from textwrap import wrap

class EncodeError(Exception): pass
class DecodeError(Exception): pass

class BaseCodec:
    def __init__(self):
        self.plainalpha = list('abcdefghijklmnopqrstuvwxyz1234567890 -=[]\\;\',./!@#$%^&*()_+{}|:\"<>?')
        
        cipher_ints = list(range(10, len(self.plainalpha) + 10))
        self.cipheralpha = [str(v) for v in cipher_ints]

    def encode(self, plaintext: str) -> str:
        try:
            encoded = []
            for letter in plaintext.lower():
                letter = self.cipheralpha[self.plainalpha.index(letter)]
                encoded.append(letter)
            return ''.join(encoded)
        except:
            raise EncodeError

    def decode(self, ciphertext: str) -> str:
        try:
            decoded = []
            for letter in wrap(ciphertext.lower(), 2):
                letter = self.plainalpha[self.cipheralpha.index(letter)]
                decoded.append(letter)
            return ''.join(decoded)
        except:
            raise DecodeError

