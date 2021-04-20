from __future__ import annotations

import functools
import multiprocessing

import asyncpg
from sanic import Blueprint, HTTPResponse, Request, text

bp = Blueprint('debug', url_prefix='debug')


@bp.route('db')
async def select(request: Request) -> HTTPResponse:
    pool: asyncpg.Pool = request.app.ctx.pool
    async with pool.acquire() as conn:
        conn: asyncpg.Connection
        name = request.args.get('name')
        if name:
            res = await conn.fetchval("SELECT value FROM test WHERE name=$1", name) or f'No name="{name}"'

    return text(res)


def count_it(name):
    counter = multiprocessing.Value('L')

    def wrapper(afunc):
        @functools.wraps(afunc)
        async def wrapped(*args, **kwargs):
            nonlocal counter
            with counter.get_lock():
                counter.value += 1
            return await afunc(*args, **kwargs)

        return wrapped

    @bp.route(f'count/{name}')
    async def count_view(request: Request) -> HTTPResponse:
        nonlocal counter

        if 'reset' in request.args:
            with counter.get_lock():
                counter.value = 0
        return text(str(counter.value))

    return wrapper
