import os
import re

class ProfanityChecker:
    def __init__(self, profanity_dir="config/profanity") -> None:
        self.profanity_set = set()
        self._load_profanity_words(profanity_dir)

    def _load_profanity_words(self, directory:str) -> None:
        for filename in os.listdir(directory):
            filepath = os.path.join(directory, filename)
            if os.path.isfile(filepath):
                with open(filepath, "r", encoding="utf-8") as file:
                    for line in file:
                        word = line.strip().lower()
                        if word:
                            self.profanity_set.add(word)

    def contains_profanity(self, text:str) -> bool:
        words = re.findall(r"\b\w+\b", text.lower())
        return any(word in self.profanity_set for word in words)

pchecker = ProfanityChecker()

def check_profanity(text: str) -> bool:
    return pchecker.contains_profanity(text)
