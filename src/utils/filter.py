from normalize import normalize
from collections import namedtuple
from re import sub, IGNORECASE

Result = namedtuple("Result", ["message", "changed"])
LETTERS = ["abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ"]


class MessageFilter:
    def __init__(self, words: str):
        self.words = [word.lower() for word in words]

    def add(self, word: str) -> bool:
        if word.lower() in self.words:
            return False
        self.words.append(word.lower())
        return True

    def remove(self, word: str) -> bool:
        if word.lower() in self.words:
            self.words.remove(word.lower())
            return True
        return False

    def __call__(self, message: str) -> Result:
        check = normalize(message).lower()
        changed = False

        check = "".join([l for l in check if l in LETTERS])

        check = check.split(" ")

        for word in self.words:
            if word in check:
                message = sub(word, "#"*len(word), message, IGNORECASE)
                changed = True

        return Result(message, changed)
