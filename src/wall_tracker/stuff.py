from django.http import JsonResponse
from rest_framework.status import HTTP_200_OK, HTTP_404_NOT_FOUND, \
    HTTP_500_INTERNAL_SERVER_ERROR, HTTP_405_METHOD_NOT_ALLOWED
import os
from pathlib import Path
import logging
import glob


class Color:
    off = '\033[0m'
    black = '\033[0;30m'
    red = '\033[0;31m'
    green = '\033[0;32m'
    yellow = '\033[0;33m'
    blue = '\033[0;34m'
    purple = '\033[0;35m'
    cyan = '\033[0;36m'
    white = '\033[0;37m'


def _setup_loggers(log_level, deps_log_level, log_format):
    app_dir = Path(__file__).resolve().parent
    logging.basicConfig(level=log_level, format=log_format)
    ours = list(f'{app_dir.name}.{Path(fn).stem}' for fn in glob.glob(str(app_dir / '*.py'))) + ['__main__', app_dir.name]
    for name in logging.root.manager.loggerDict:
        if name in ours:
            continue
        logging.getLogger(name).setLevel(deps_log_level)


def setup_logger():
    c = Color
    log_no_color = bool(int(os.environ.get('LOG_NO_COLOR', '0')))
    log_format = ('[%(asctime)s]:%(levelname)-5s:: %(message)s -- {%(filename)s:%(lineno)d:(%(funcName)s)}' 
                if log_no_color else
                f'[{c.white}%(asctime)s{c.off}]:{c.yellow}%(levelname)-5s{c.off}::{c.green} %(message)s {c.white}-- {c.yellow}{{{c.blue}%(filename)s{c.off}:{c.cyan}%(lineno)d{c.off}:({c.purple}%(funcName)s{c.off}){c.yellow}}}{c.off}')        
    log_level = os.environ.get('LOG_LEVEL', 'INFO')
    deps_log_level = os.environ.get('DEPS_LOG_LEVEL', 'INFO')
    _setup_loggers(log_level, deps_log_level, log_format)


def make_response(request_id, status=HTTP_200_OK, data=None, result='success', desc=None):
    if desc is None:
        return JsonResponse(data=dict(data=dict() if data is None else data, 
                                      meta=dict(id=request_id, result=result)),
                            status=status)

    return JsonResponse(data=dict(data=dict() if data is None else data, 
                                  meta=dict(id=request_id, result=result, desc=desc)),
                        status=status)


def make_404_not_found_response(request_id):
    return make_response(request_id=request_id, 
                            result='error', 
                            desc='Not found', 
                            status=HTTP_404_NOT_FOUND)


def make_400_bad_request_response(request_id):
    return make_response(request_id=request_id, 
                            result='error', 
                            desc='Bad request', 
                            status=HTTP_400_BAD_REQUEST)


def make_500_internal_server_error_response(request_id):
    return make_response(request_id=request_id, 
                            result='error', 
                            desc='Internal server error', 
                            status=HTTP_500_INTERNAL_SERVER_ERROR)
