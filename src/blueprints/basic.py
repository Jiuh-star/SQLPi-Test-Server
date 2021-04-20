from __future__ import annotations

import operator
import random

from sanic import Blueprint, Request, HTTPResponse, text

from . import debug

bp = Blueprint('basic', url_prefix='basic')

random_target = str(random.randint(1, int(1E12)))


@bp.get('echo')
async def echo(request: Request) -> HTTPResponse:
    return text(request.args.get('msg', ''))


@bp.get('compare/<comp:string>')
@debug.count_it('compare')
async def compare(request: Request, comp: str) -> HTTPResponse:
    val = request.args.get('val')
    target_ = request.args.get('target_', random_target)

    if not val.isdigit():
        return text('val is not a integer.')
    if not target_.isdigit():
        return text('target_ is not a integer.')

    val = int(val)
    target_ = int(target_)
    try:
        res = getattr(operator, comp)(val, target_)
    except AttributeError:
        return text('comp is not a legal comp (gt, ge, lt, le, eq, ne).')

    return text(str(res))


@debug.bp.route('target')
async def target(request: Request) -> HTTPResponse:
    return text(random_target)
