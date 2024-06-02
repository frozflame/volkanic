#!/usr/bin/env python3
# coding: utf-8
from concurrent.futures import ThreadPoolExecutor, ProcessPoolExecutor
from random import randrange

from volkanic import utils
from volkanic.compat import cached_property
# noinspection PyProtectedMember
from volkanic.utils import _hide_first_level_relpath
from volkanic.utils import per_process_cached_property


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
        print('error raised as expeced:', e)
    else:
        print('error not raised:', p)
        raise RuntimeError('error not raised')


class T:
    @cached_property
    def prop1(self):
        return randrange(1000 * 1000)

    @per_process_cached_property
    def prop2(self):
        return randrange(1000 * 1000)


def test_cached_property():
    t = T()
    assert t.prop1 == t.prop1
    assert t.prop2 == t.prop2
    tx = ThreadPoolExecutor(max_workers=4)
    px = ProcessPoolExecutor(max_workers=4)
    args = [t] * 100, ['prop2'] * 100
    tvals = set(tx.map(getattr, *args))
    pvals = set(px.map(getattr, *args))
    assert len(tvals) == 1, tvals
    assert len(pvals) > 98, pvals


if __name__ == '__main__':
    test_hide_first_level_relpath()
    test_cached_property()
