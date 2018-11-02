#!/usr/bin/env python3
# coding: utf-8

from __future__ import unicode_literals, print_function

import volkanic


def run(prog, _):
    import sys
    for ix, arg in enumerate(sys.argv):
        print(ix, repr(arg), sep='\t')
    print('\nprog:', repr(prog), sep='\t', file=sys.stderr)


run_command_conf = volkanic.CommandConf.run

registry = volkanic.CommandRegistry({
    'volkanic.default': 'argv',
    'volkanic.default:run_command_conf': 'runconf'
})
