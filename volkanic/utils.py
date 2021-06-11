#!/usr/bin/env python3
# coding: utf-8

import os
import importlib


def query_attr(obj, *names):
    for x in names:
        obj = getattr(obj, x)
    return obj


subattr = query_attr


def load_symbol(symbolpath):
    parts = symbolpath.split(':', 1)
    symbol = importlib.import_module(parts.pop(0))
    if parts:
        symbol = query_attr(symbol, *parts[0].split('.'))
    return symbol


def load_variables(*contexts):
    import re
    scope = {}
    for ctx in contexts:
        if not isinstance(ctx, dict):
            ctx = {re.split(r'[.:]', x)[-1]: x for x in ctx}
        for key, val in ctx.items():
            scope[key] = load_symbol(val)
    return scope


def abs_path_join(*paths):
    if not paths:
        msg = 'abs_path_join() requires at least 1 argument'
        raise TypeError(msg)
    if paths[0].startswith('~'):
        paths = list(paths)
        paths[0] = os.path.expanduser(paths[0])
    path = os.path.join(*paths)
    return os.path.abspath(path)


def abs_path_join_and_mkdirs(*paths):
    path = abs_path_join(*paths)
    if paths[-1].endswith('/'):
        os.makedirs(path, exist_ok=True)
    else:
        os.makedirs(os.path.split(path)[0], exist_ok=True)
    return path
