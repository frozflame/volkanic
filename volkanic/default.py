#!/usr/bin/env python3
# coding: utf-8

from __future__ import unicode_literals, print_function

import importlib
import os
import sys

import volkanic


def _linux_open(path):
    import subprocess
    subprocess.run(['xdg-open', path])


def _macos_open(path):
    import subprocess
    subprocess.run(['open', path])


def _windows_open(path):
    getattr(os, 'startfile')(path)


def desktop_open(*paths):
    import platform
    osname = platform.system().lower()
    if osname == 'darwin':
        handler = _macos_open
    elif osname == 'windows':
        handler = _windows_open
    else:
        handler = _linux_open
    for path in paths:
        handler(path)


def where(name):
    mod = importlib.import_module(name)
    path = getattr(mod, '__file__', 'NotAvailable')
    dir_, filename = os.path.split(path)
    if filename.startswith('__init__.'):
        return dir_
    return path


def where_site_packages():
    for name in ['pip', 'easy_install']:
        try:
            return os.path.split(where(name))[0]
        except ModuleNotFoundError:
            continue
    for p in sys.path:
        if p.endswith('site-packages'):
            return p


def run_where(_, args):
    if not args:
        return print(where_site_packages() or '')
    for arg in args:
        try:
            path = where(arg)
            print(arg, path, sep='\t')
        except ModuleNotFoundError:
            print(arg, 'ModuleNotFoundError', sep='\t')


def run_argv_debug(prog, _):
    import sys
    for ix, arg in enumerate(sys.argv):
        print(ix, repr(arg), sep='\t')
    print('\nprog:', repr(prog), sep='\t', file=sys.stderr)


def run_desktop_open(_, args):
    args = args or ('.',)
    desktop_open(*args)


run_command_conf = volkanic.CommandConf.run

registry = volkanic.CommandRegistry.from_entries({
    'volkanic.default:run_where': 'where',
    'volkanic.default:run_argv_debug': 'a',
    'volkanic.default:run_desktop_open': 'o',
    'volkanic.default:run_command_conf': 'runconf',
})
