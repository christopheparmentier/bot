from abc import ABCMeta

from discord.ext.commands import CogMeta

from bot.utils.redis_cache import RedisCache

__all__ = ['RedisCache', 'CogABCMeta']


class CogABCMeta(CogMeta, ABCMeta):
    """Metaclass for ABCs meant to be implemented as Cogs."""

    pass


def has_lines(string: str, count: int) -> bool:
    """Return True if `string` has at least `count` lines."""
    split = string.split("\n", count - 1)

    # Make sure the last part isn't empty, which would happen if there was a final newline.
    return split[-1] and len(split) == count
