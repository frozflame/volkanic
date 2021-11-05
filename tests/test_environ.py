#!/usr/bin/env python3
# coding: utf-8

import volkanic
from volkanic import utils
from volkanic.environ import GIMixinDirs


class GlobalInterface(volkanic.GlobalInterface, GIMixinDirs):
    default_config = {'data_dir': '/data/local/volkanic'}
    package_name = 'os.path'


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
    _eq(GlobalInterface.package_name, 'os.path')
    _eq(GlobalInterface.project_name, 'os-path')
    _eq(GlobalInterface.identifier, 'os_path')

    class GI1(GlobalInterface):
        package_name = 'hello_world.demo'

    _eq(GI1.project_name, 'hello-world-demo')
    _eq(GI1.identifier, 'hello_world_demo')


def test_under_dir():
    _eq(volk_gi.under_package_dir('a', 'b'),
        volk_gi.under_package_dir('a/b'))
    _eq(volk_gi.under_package_dir(),
        utils.under_parent_dir(volkanic.__file__))
    _eq(test_gi.under_data_dir(),
        '/data/local/volkanic')
