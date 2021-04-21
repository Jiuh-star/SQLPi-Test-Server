from __future__ import annotations

import asyncio as aio
from hashlib import sha1
from pathlib import Path
from random import random

import asyncpg
import click
from sanic import Sanic

import blueprints

app = Sanic('sqlpi-test-server')

_CONN_DSN = 'postgres://{user}:{password}@{host}:{port}/{database}'.format(
    user='test',
    password='test',
    host='localhost',
    port='5432',
    database='test',
)
STATIC_PATH = Path(__file__).resolve().parent.parent / 'static'

app.static('/', 'static/README.txt')

app.blueprint(blueprints.bp_group)


@app.before_server_start
async def setup_db(app_, loop):
    app_.ctx.pool = await asyncpg.create_pool(
        dsn=_CONN_DSN,
        loop=loop
    )


@app.after_server_stop
async def close_db(app_, loop):
    await app_.ctx.pool.close()


@click.group()
def cli():
    pass


@cli.command(help='Initiate the database')
def init_db():
    async def _init_db():
        conn: asyncpg.Connection = await asyncpg.connect(dsn=_CONN_DSN)

        with open(STATIC_PATH / 'alice_in_wonderland.txt') as f:
            story = f.read()

        async with conn.transaction():
            await conn.execute("DROP TABLE IF EXISTS test")
            await conn.execute("CREATE TABLE test(name varchar(20), value text)")
            await conn.execute("INSERT INTO test (name, value) VALUES ('random', $1)",
                               (sha1(str(random()).encode('ascii')).hexdigest()))
            await conn.execute("INSERT INTO test (name, value) VALUES ('story', $1)", story)
            await conn.execute("INSERT INTO test VALUES('utf-8', '这是一段测试文本')")
        await conn.close()

    aio.get_event_loop().run_until_complete(_init_db())


@cli.command(help='Run server')
@click.option('--host', default='127.0.0.1', help='The interface to bind to server.')
@click.option('--port', default=8000, help='The port to bind to server.')
@click.option('--debug/--no-debug', default=False, help='Run under debug or not.')
@click.option('--workers', default=1, help='The subprocess that app used.')
@click.option('--log/--no-log', default=True, help='Access log or not')
def run(host, port, debug, workers, log):
    # FIXME: workers=1 should be set on Windows as sanic's Windows support is currently "experimental"
    app.run(host=host, port=port, debug=debug, workers=workers, access_log=log)


if __name__ == '__main__':
    cli()
