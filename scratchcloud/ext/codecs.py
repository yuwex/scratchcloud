from textwrap import wrap
from ..errors import EncodeError, DecodeError

class BaseCodec:
    """A codec that encodes and decodes data to and from n-length numbers.
    
    :param plainalpha: The alphabet that will be used for encoding to number
    :type plainalpha: str | list[str]
    :param offset: The number where cipheralpha will start
    :type offset: int
    :param force_lowecase: If all characters should be forced lowercase
    :type force_lowecase: bool
    :param places_per_character: the length of each item in cipher ints. Numbers in cipheralpha smaller than this value will begin with 0s.
    :type places_per_character: int

    :raises TypeError: If Cipheralpha has too large numbers.
    """

    def __init__(self, plainalpha: str | list[str] = 'abcdefghijklmnopqrstuvwxyz1234567890 -=[]\\;\',./!@#$%^&*()_+{}|:\"<>?', offset: int = 10, force_lowercase: bool = True, places_per_character: int = 2):
        self.force_lowercase = force_lowercase
        self.places_per_character = places_per_character
        
        if isinstance(plainalpha, list):
            self.plainalpha = plainalpha
        else:
            self.plainalpha = list(plainalpha)

        self.cipheralpha = []

        cipher_ints = list(range(offset, len(self.plainalpha) + offset))
        for number in cipher_ints:
            number = str(number)

            if len(number) > self.places_per_character:
                raise TypeError('Cipheralpha has too many numbers. Remove characters from the specified alphabet or increase places_per_character.')
            elif len(number) != self.places_per_character:
                zeros = (self.places_per_character - len(number)) * '0'
                self.cipheralpha.append(f'{zeros}{number}')
            else:
                self.cipheralpha.append(number)        

    def encode(self, plaintext: str) -> str:
        """A method that encodes plaintext.

        :param plaintext: The text that will be decoded
        :type plaintext: str

        :raises EncodeError: If unable to encode. Likely due to characters not included in plainalpha.

        :rtype: str
        """

        if self.force_lowercase:
            plaintext = plaintext.lower()
        
        encoded = []
        for letter in plaintext:
            
            if letter not in self.plainalpha:
                raise EncodeError(f'plainalpha characters does not contain {letter}')

            letter = self.cipheralpha[self.plainalpha.index(letter)]
            encoded.append(letter)
        return ''.join(encoded)

    def decode(self, ciphertext: str | int) -> str:
        """A method that decodes ciphertext.

        :param ciphertext: The text that will be encoded
        :type ciphertext: str | int

        :raises EncodeError: If unable to encode. Likely due to characters not included in plainalpha.

        :rtype: str
        """

        if self.force_lowercase:
            ciphertext = ciphertext.lower()
        
        decoded = []
        for number in wrap(ciphertext, self.places_per_character):
            if number not in self.cipheralpha:
                raise DecodeError(f'cipheralpha does not contain number {number}')

            number = self.plainalpha[self.cipheralpha.index(number)]
            decoded.append(number)
        return ''.join(decoded)
            

