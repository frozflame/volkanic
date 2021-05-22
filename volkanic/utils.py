#!/usr/bin/env python3
# coding: utf-8
import importlib


def subattr(obj, *names):
    for x in names:
        obj = getattr(obj, x)
    return obj


def load_symbol(symbolpath):
    parts = symbolpath.split(':', 1)
    symbol = importlib.import_module(parts.pop(0))
    if parts:
        symbol = subattr(symbol, *parts[0].split('.'))
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