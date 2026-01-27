import os
import re
from . import logging as log

class ProfanityChecker:
    '''
    Class that checks profanity
    '''
    def __init__(self, profanity_dir: str = "config/profanity") -> None:
        '''
        Initializes a ProfanityChecker class

        Parameters
        ----------
        profanity_dir : str, optional
            Path to profanity dir (default is 'config/profanity')
        '''
        self.profanity_set = set()
        self._load_profanity_words(profanity_dir)

    def _load_profanity_words(self, directory:str) -> None:
        '''
        Load words into a set

        Parameters
        ----------
        directory : str
            Path to profanity dir
        '''
        for filename in os.listdir(directory):
            filepath = os.path.join(directory, filename)
            if os.path.isfile(filepath):
                with open(filepath, "r", encoding="utf-8") as file:
                    for line in file:
                        word = line.strip().lower()
                        if word:
                            self.profanity_set.add(word)

    def contains_profanity(self, text:str) -> bool:
        '''
        Checks if the text contains profanity

        Parameters
        ----------
        text : str
            Text to check

        Returns
        -------
        bool
            Whether it contains profanity or not
        '''
        words = re.findall(r"\b\w+\b", text.lower())
        return any(word in self.profanity_set for word in words)

def init_checker():
    '''
    Initializes profanity checker
    '''
    try:
        global pchecker
        pchecker = ProfanityChecker()
    except:
        log.warn("FAILED TO INITIALIZE PROFANITY CHECKER",name="profanity")

def check_profanity(text: str) -> bool:
    '''
    Checks if the text contains profanity

    Parameters
    ----------
    text : str
        Text to check

    Returns
    -------
    bool
        Whether it contains profanity or not
    '''
    return pchecker.contains_profanity(text)
