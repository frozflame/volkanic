#!/usr/bin/env python3
# coding: utf-8

import importlib

from volkanic.environ import GlobalInterface
from volkanic.introspect import find_all_plain_modules

gi = GlobalInterface()


def test_importability():
    for dotpath in find_all_plain_modules(gi.under_project_dir()):
        if dotpath.startswith('volkanic.'):
            print(dotpath)
            importlib.import_module(dotpath)


if __name__ == '__main__':
    test_importability()
