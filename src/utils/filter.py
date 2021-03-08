from normalize import normalize
from typing import Tuple
from collections import namedtuple

Result = namedtuple("Result", ["message", "changed"])


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
        message = normalize(message).lower()
        changed = False

        for word in self.words:
            if word in message:
                message.replace("word", "#"*len(word))
                changed = True

        return Result(message, changed)
