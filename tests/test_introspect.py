#!/usr/bin/env python3
# coding: utf-8

from volkanic import introspect
from volkanic.introspect import ErrorBase


def test_path_formatters():
    vals = [
        introspect.format_class_path(dict),
        introspect.format_function_path(dict.pop),
        introspect.format_function_path(lambda: 1),
    ]
    for v in vals:
        print(v)


def test_errorbase():
    eb = ErrorBase('something wrong')
    d = eb.to_dict()
    assert ErrorBase.from_dict(d).to_dict() == d
    eb = ErrorBase('bad-request', 'EB-1234')
    d = eb.to_dict()
    assert ErrorBase.from_dict(d).to_dict() == d


if __name__ == '__main__':
    test_path_formatters()
