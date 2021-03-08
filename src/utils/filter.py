from normalize import normalize
from typing import Tuple
from collections import namedtuple

Result = namedtuple("Result", ["message", "changed"])


class MessageFilter:
    def __init__(self, words: str):
        self.words = words

    def add(self, word: str) -> bool:
        if word in self.words:
            return False
        self.words.append(word)
        return True

    def remove(self, word: str) -> bool:
        if word in self.words:
            self.words.remove(word)
            return True
        return False

    def __call__(self, message: str) -> Result:
        message = normalize(message)
        changed = False

        for word in self.words:
            if word in message:
                message.replace("word", "#"*len(word))
                changed = True

        return Result(message, changed)
