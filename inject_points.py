from itertools import chain
from random import randint
from time import sleep

from db import unsafe_query

__all__ = ['inject_simple', 'inject_waf', 'inject_latency']


def binary_result(func):
    def _wrapper(*args, **kwargs):
        return True if list(chain.from_iterable(*func(*args, **kwargs))) else False

    return _wrapper


def _waf(*params):
    """Not allowed any comparison operator"""
    for param in params:
        if any(comp in param for comp in ('>', '<', '=', '!')):
            return False
    return True


def _common_inject(inject):
    sql = "SELECT value from test WHERE name='?' LIMIT 0,1"
    result = unsafe_query(sql, inject)
    return result


@binary_result
def inject_simple(inject):
    return _common_inject(inject)


@binary_result
def inject_waf(inject):
    return _waf(inject) and _common_inject(inject)


@binary_result
def inject_latency(inject):
    sleep(randint(3, 5))
    return _common_inject(inject)
