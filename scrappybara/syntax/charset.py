import scrappybara.config as cfg
from scrappybara.utils.files import load_pkl_file, save_pkl_file
from scrappybara.utils.text import LETTERS, UPPERCASE_LETTERS, DIGITS


class Charset(object):

    def __init__(self):
        self.__filepath = cfg.DATA_DIR / 'models/char_codes.pkl'
        self.__char_code = None  # Char => code
        self.__unk_code = None  # Positive integer

    def __len__(self):
        return len(self.__char_code) + 1

    def __getitem__(self, char):
        """Returns the code of a char"""
        try:
            return self.__char_code[char]
        except KeyError:
            return self.__unk_code

    def load(self):
        self.__char_code = load_pkl_file(self.__filepath)
        self.__unk_code = max(self.__char_code.values()) + 1
        return self

    def save(self):
        """Save dictionary of char=>idx as a pkl file"""
        special_chars = set('`~!@#$£€%^&*()-_=+[{]}\\|;:\'",<.>/?')
        padding_chars = set('†‡ʃʄ')
        chars = LETTERS | UPPERCASE_LETTERS | DIGITS | special_chars | padding_chars
        char_code = {char: idx for idx, char in enumerate(chars)}
        save_pkl_file(char_code, self.__filepath)
