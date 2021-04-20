from __future__ import annotations

import asyncio as aio
import random

import asyncpg
import sanic.exceptions
from asyncpg import Pool
from sanic import Blueprint, Request, text, HTTPResponse

from . import debug

QUERY_SQL = "SELECT value FROM test WHERE name='?'"

bp = Blueprint('inject-point', url_prefix='inject')


def binary_query_result(afunc):
    async def wrapped(*args, **kwargs):
        try:
            return text('True') if await afunc(*args, **kwargs) else text('False')
        except asyncpg.PostgresError:
            return text('False')

    return wrapped


@debug.count_it('inject')
async def unsafe_query(pool: Pool, sql: str, *params):
    params = iter(params)

    sql = ''.join(map(lambda c: c if c != '?' else str(next(params, '?')), sql))

    async with pool.acquire() as connection:
        async with connection.transaction():
            return await connection.fetchval(sql)


@bp.route('error/simple')
async def error_simple_inject_point(request: Request) -> HTTPResponse:
    if 'inject' not in request.args:
        return text(QUERY_SQL)

    try:
        res = await unsafe_query(request.app.ctx.pool, QUERY_SQL, request.args.get('inject'))
    except asyncpg.PostgresError as e:
        res = e
    return text(str(res))


@bp.route('blind/waf')
@binary_query_result
async def blind_waf_inject_point(request: Request):
    if 'inject' not in request.args:
        return text(QUERY_SQL)

    inject = str(request.args.get('inject'))
    if any(k in inject for k in ('>', '>=', '<', '<=', '==', '!=', '<>')):
        return False

    return await unsafe_query(request.app.ctx.pool, QUERY_SQL, inject)


@bp.route('blind/latency')
@binary_query_result
async def blind_latency_inject_point(request: Request):
    if 'inject' not in request.args:
        return text(QUERY_SQL)

    await aio.sleep(2)

    return await unsafe_query(request.app.ctx.pool, QUERY_SQL, request.args.get('inject'))


@bp.route('blind/bad-net')
@binary_query_result
async def blind_bad_bet_inject_point(request: Request) -> HTTPResponse:
    if 'inject' not in request.args:
        return text(QUERY_SQL)

    ticket = random.randint(0, 4)
    if ticket == 0:
        raise sanic.exceptions.ServiceUnavailable('ServiceUnavailable')

    return await unsafe_query(request.app.ctx.pool, QUERY_SQL, request.args.get('inject'))
