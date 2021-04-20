from sanic import Blueprint

from . import basic
from . import debug
from . import inject_point

bp_group = Blueprint.group(basic.bp, debug.bp, inject_point.bp)
