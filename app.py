import random
import threading
from textwrap import dedent

try:
    from gevent import monkey
    from gevent.pywsgi import WSGIServer

    monkey.patch_all()
finally:
    pass

from flask import Flask, redirect, url_for, request, Response

import db
from inject_points import *

RANDOM_VALUE = random.randint(1, 0xFFFFFF)
SQL_COMP_PYTHON_COMP = {
    '>': '>',
    '>=': '>=',
    '<': '<',
    '<=': '<=',
    '=': '==',
    '!=': '!=',
}
INJECT_APP_INJECT_POINT = {
    'simple': inject_simple,
    'waf': inject_waf,
    'latency': inject_latency,
}

app = Flask(__name__)
db.init_app(app)

lock = threading.Lock()
name_count = {}


def safe_count(name, reset=False):
    global name_count
    with lock:
        try:
            name_count[name] += 1
        except KeyError:
            name_count[name] = 1
        if reset:
            name_count[name] = 0
    return name_count[name]


@app.before_request
def request_count():
    safe_count('request_num')


@app.route('/')
def index():
    return redirect(url_for('static', filename='README.txt'))


@app.route('/echo')
def echo():
    msg = request.args.get('msg', '')
    app.logger.info(f'URL /echo received message "{msg}".')
    return msg


@app.route('/compare/<comp>')
def compare(comp):
    safe_count('compare_num')

    comp = SQL_COMP_PYTHON_COMP[comp]
    val = request.args.get('val', 0)
    target_val = request.args.get('target', RANDOM_VALUE)
    expression = f'{target_val} {comp} {val}'
    result = eval(expression)
    app.logger.info(f'URL /compare/<comp> eval expression "{expression}" and result is {result}')
    return str(result)


@app.route('/inject/<app_name>')
def inject(app_name):
    safe_count('inject_num')

    inject_ = request.args.get('inject', '')
    if not inject_:
        return "test sql is 'SELECT value from test WHERE name='inject' LIMIT 0,1'"

    app_name = app_name or 'simple'
    app.logger.info(f'URL /inject/<app_> use app {app_name} with inject "{inject_}"')

    app_ = INJECT_APP_INJECT_POINT[app_name]

    result = app_(inject_)
    app.logger.info(f'URL /inject/<app_> returns {result}')
    return str(result)


@app.route('/debug/target')
def debug_target():
    app.logger.info(f'URL /debug/target returns {RANDOM_VALUE}')
    return str(RANDOM_VALUE)


@app.route('/debug/count')
def debug_count():
    global name_count
    if 'reset' in request.args.keys():
        app.logger.info(f'URL /debug/target reset count')
        safe_count('inject_num', reset=True)
        safe_count('compare_num', reset=True)
        safe_count('request_num', reset=True)
    app.logger.info(
        f'URL /debug/count returns '
        f'inject: {name_count.get("inject_num", 0)}, '
        f'compare: {name_count.get("compare_num", 0)}, '
        f'request: {name_count.get("request_num", 0)}')
    return Response((
        f'Inject Count: {name_count.get("inject_num", 0)}\n'
        f'Compare Count: {name_count.get("compare_num", 0)}\n'
        f'Request Count: {name_count.get("request_num", 0)}\n'
    ), mimetype='text/plain')


@app.route('/debug/db')
def debug_db():
    name = request.args.get('name', 'random')
    app.logger.info(f'URL /debug/db query name {name}')
    return Response(''.join(debug_query(name)[0]), mimetype='text/plain')


if __name__ == '__main__':
    print(dedent("""
         _____  _____  __     _____  _ 
        |   __||     ||  |   |  _  ||_|
        |__   ||  |  ||  |__ |   __|| |
        |_____||__  _||_____||__|   |_|
                  |__|
        ==============================="""))
    print('SQLPi Test Server start.')

    import logging

    app.logger.level = logging.INFO

    http_server = WSGIServer(('127.0.0.1', 5000), app, log=app.logger)
    try:
        http_server.serve_forever()
    except KeyboardInterrupt:
        print("SQLPi Test Server stop.")
