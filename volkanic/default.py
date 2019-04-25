#!/usr/bin/env python3
# coding: utf-8

from __future__ import unicode_literals, print_function

import volkanic


def _linux_open(path):
    import subprocess
    subprocess.run(['xdg-open', path])


def _macos_open(path):
    import subprocess
    subprocess.run(['open', path])


def _windows_open(path):
    import os
    os.startfile(path)


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


def run_argv_debug(prog, _):
    import sys
    for ix, arg in enumerate(sys.argv):
        print(ix, repr(arg), sep='\t')
    print('\nprog:', repr(prog), sep='\t', file=sys.stderr)


def run_desktop_open(_, args):
    desktop_open(*args)


run_command_conf = volkanic.CommandConf.run

registry = volkanic.CommandRegistry({
    'volkanic.default:run_argv_debug': 'a',
    'volkanic.default:run_desktop_open': 'o',
    'volkanic.default:run_command_conf': 'runconf',
})
