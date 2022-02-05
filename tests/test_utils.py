#!/usr/bin/env python3
# coding: utf-8

from volkanic import utils

# noinspection PyProtectedMember
from volkanic.utils import _hide_first_level_relpath


def assert_equal(a, b):
    assert a == b, (a, b)


def test_under_home_dir_hidden():
    assert_equal(
        utils.under_home_dir('.a/b/c'),
        utils.under_home_dir_hidden('a/b/c'),
    )


def test_hide_first_level_relpath():
    assert_equal(
        _hide_first_level_relpath('a//b/../c'),
        '.a/c'
    )
    assert_equal(
        _hide_first_level_relpath('.a//b/../c'),
        '.a/c'
    )
    assert_equal(
        _hide_first_level_relpath('..a//b/../c'),
        '..a/c'
    )
    assert_equal(
        _hide_first_level_relpath('/a//b/../c'),
        '/a/c'
    )
    assert_equal(
        _hide_first_level_relpath('./a//b/../c'),
        '.a/c'
    )
    try:
        p = _hide_first_level_relpath('../a/b/../c')
    except ValueError as e:
        print('error raised:', e)
    else:
        print('error not raised:', p)
        raise RuntimeError('error not raised')


if __name__ == '__main__':
    test_hide_first_level_relpath()
