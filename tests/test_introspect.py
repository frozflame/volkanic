#!/usr/bin/env python3
# coding: utf-8

from volkanic import introspect


def test_path_formatters():
    vals = [
        introspect.format_class_path(dict),
        introspect.format_function_path(dict.pop),
        introspect.format_function_path(lambda: 1),
    ]
    for v in vals:
        print(v)


if __name__ == '__main__':
    test_path_formatters()
