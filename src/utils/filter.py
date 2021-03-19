from normalize import normalize
from collections import namedtuple
from re import sub, IGNORECASE

Result = namedtuple("Result", ["message", "changed", "tokens"])
LETTERS = "abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ"

with open("./static/words.txt") as f:
    init_words = set([word.strip() for word in f.readlines()])


class MessageFilter:
    def __init__(self, words: str):
        self.words = set([word.lower() for word in words]) | init_words

    def add(self, word: str) -> bool:
        if word.lower() in self.words:
            return False
        self.words.add(word.lower())
        return True

    def remove(self, word: str) -> bool:
        if word.lower() in init_words:
            return False
        if word.lower() in self.words:
            self.words.remove(word.lower())
            return True
        return False

    def __call__(self, message: str) -> Result:
        check = normalize(message).lower()
        changed = False

        check = "".join([l for l in check if l in LETTERS])

        check = check.split(" ")

        tokens = []

        for word in self.words:
            if word in check:
                message = sub(word, "#" * len(word), message, IGNORECASE)
                changed = True
                tokens.append(word)

        return Result(message, changed, tokens)
