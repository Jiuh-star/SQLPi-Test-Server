import random

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

inject_num = 0
request_num = 0
compare_num = 0


@app.before_request
def request_count():
    global request_num
    request_num += 1


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
    global compare_num
    compare_num += 1

    comp = SQL_COMP_PYTHON_COMP[comp]
    val = request.args.get('val', 0)
    target_val = request.args.get('target', RANDOM_VALUE)
    expression = f'{target_val} {comp} {val}'
    result = eval(expression)
    app.logger.info(f'URL /compare/<comp> eval expression "{expression}" and result is {result}')
    return str(result)


@app.route('/inject/<app_name>')
def inject(app_name):
    global inject_num
    inject_num += 1

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
    global inject_num, compare_num, request_num
    if 'reset' in request.args.keys():
        app.logger.info(f'URL /debug/target reset count')
        inject_num, compare_num, request_num = 0, 0, 0
    app.logger.info(f'URL /debug/count returns inject: {inject_num}, compare: {compare_num}, request: {request_num}')
    return Response((
        f'Inject Count: {inject_num}\n'
        f'Compare Count: {compare_num}\n'
        f'Request Count: {request_num}\n'
    ), mimetype='text/plain')


@app.route('/debug/db')
def debug_db():
    name = request.args.get('name', 'random')
    app.logger.info(f'URL /debug/db query name {name}')
    return Response(''.join(debug_query(name)[0]), mimetype='text/plain')


if __name__ == '__main__':
    app.run(debug=True)
