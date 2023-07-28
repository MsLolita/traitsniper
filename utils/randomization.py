import asyncio
import random


async def delay(from_: float = None, to: float = None):
    if from_ is None:
        from_ = 30
        to = 50
    elif to is None:
        to = from_ * 1.7

    await asyncio.sleep(random.uniform(from_, to))


def random_bool(weights: tuple = (2, 1)):
    return random.choices([True, False], weights=weights)[0]
