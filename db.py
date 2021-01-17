from hashlib import sha1
from pathlib import PurePath
from random import random

import click
import pymysql
from flask import g
from flask.cli import with_appcontext

RES_ROOT = PurePath(__file__).parent.joinpath('static/')

connect_config = {
    'host': 'localhost',
    'user': 'test',
    'password': 'test',
    'db': 'test',
    'charset': 'utf8mb4'
}


def init_db():
    db = get_db()
    c = db.cursor()
    with open(RES_ROOT.joinpath('alice_in_wonderland.txt')) as f:
        c.execute("DROP TABLE IF EXISTS test")
        c.execute("CREATE TABLE test(name varchar(20), value mediumtext)")
        c.execute("INSERT INTO test VALUES('random', %s)", (sha1(str(random()).encode('ascii')).hexdigest(),))
        c.execute("INSERT INTO test VALUES('story', %s)", (f.read(),))
        c.execute("INSERT INTO test VALUES('utf-8', '这是一段测试文本')".encode('utf8'))
    c.close()
    db.commit()


def get_db():
    if 'db' not in g:
        g.db = pymysql.connect(**connect_config)
    return g.db


def unsafe_query(script: str, *args) -> list:
    """unsafe query for test"""
    db = get_db()
    c = db.cursor()

    for arg in args:
        script = script.replace('?', str(arg), 1)

    try:
        c.execute(script)
    finally:
        c.close()

    result = c.fetchall()

    return result


def close_db(e=None):
    db = g.pop('db', None)
    if db is not None:
        db.close()


@click.command('init-db')
@with_appcontext
def init_db_command():
    init_db()
    click.echo('Database initialized.')


def init_app(app):
    app.teardown_appcontext(close_db)
    app.cli.add_command(init_db_command)
