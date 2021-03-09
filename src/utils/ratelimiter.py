from time import time
from collections import defaultdict, namedtuple

User = namedtuple("User", ["id", "last"])
Item = namedtuple("Item", ["value", "time"])


def minmax(minval: float, maxval: float, val: float) -> float:
    return max(min(val, maxval), minval)


class AgedList:
    def __init__(self, max_age: int = 5):
        self.max_age = max_age
        self.items = []

    def clean(self):
        t = time()
        for item in self.items:
            if item.time + self.max_age < t:
                self.items.remove(item)

    def add(self, item=1):
        self.items.append(Item(item, time()))

        self.clean()

    def len(self):
        self.clean()

        return len(self.items)


class Ratelimiter:
    def __init__(self):
        self.channel_users = defaultdict(dict)
        self.channel_activity = defaultdict(AgedList)
        self.threshold = 1
        self.max_slowmode = 15
        self.min_slowmode = 1

    def message(self, user_id: int, channel: str):
        users = self.channel_users[channel]

        user = User(**users.get(user_id, {"id": user_id, "last": 0}))

        if user.last + self.threshold > time():
            return round((user.last + self.threshold) - time(), 2)

        self.channel_users[channel][user_id] = {"id": user_id, "last": time()}
        self.channel_activity[channel].add()

        length = self.channel_activity[channel].len()

        self.threshold = minmax(self.min_slowmode, self.max_slowmode, length // 4)

        return 0
