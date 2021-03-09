from re import compile, IGNORECASE
from discord import Emoji

from src.internal.bot import Bot

EMOJI = compile(r"<a?:\w{2,32}:\d{17,20}>", IGNORECASE)
NAME = compile(r"[^ :]{2,32}", IGNORECASE)
ID = compile(r"\d*")


class EmojiFixer:
    def __init__(self, bot: Bot):
        self.bot = bot

    def message(self, content: str):
        botems = {emoji.id for emoji in self.bot.emojis}

        ems = []
        for emoji in EMOJI.finditer(content):
            e = emoji.group()
            name = NAME.search(e)
            _id = ID.search(e).group()

            if _id in botems:
                continue

            for em in self.bot.emojis:
                em: Emoji
                if em.name.lower() == name.group().lower():
                    ems.append((e, f"<{'a' if em.animated else ''}:{em.name}:{em.id}>"))
                    break

        for e in ems:
            content = content.replace(e[0], e[1])

        return content
