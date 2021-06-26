#!/usr/bin/env python3
# coding: utf-8

import volkanic
from volkanic import utils


class GlobalInterface(volkanic.GlobalInterface):
    package_name = 'joker.example'


volk_gi = volkanic.GlobalInterface()
test_gi = GlobalInterface()


def _eq(a, b):
    assert a == b, a


def test_singularity():
    assert GlobalInterface() is test_gi
    assert GlobalInterface() is GlobalInterface()
    assert volkanic.GlobalInterface() is volk_gi
    assert volkanic.GlobalInterface() is volkanic.GlobalInterface()
    assert volk_gi.conf is volk_gi.conf


def test_names():
    _eq(volkanic.GlobalInterface.package_name, 'volkanic')
    _eq(volkanic.GlobalInterface.project_name, 'volkanic')
    _eq(volkanic.GlobalInterface.identifier, 'volkanic')
    _eq(GlobalInterface.package_name, 'joker.example')
    _eq(GlobalInterface.project_name, 'joker-example')
    _eq(GlobalInterface.identifier, 'joker_example')


def test_under_dir():
    _eq(volk_gi.under_package_dir('a', 'b'),
        volk_gi.under_package_dir('a/b'))
    _eq(volk_gi.under_package_dir(),
        utils.under_parent_dir(volkanic.__file__))
