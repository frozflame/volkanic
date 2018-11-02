#!/usr/bin/env python3
# coding: utf-8

from __future__ import unicode_literals, print_function

from volkanic.system import CommandRegistry as _CReg


def run(prog, _):
    import sys
    for ix, arg in enumerate(sys.argv):
        print(ix, repr(arg), sep='\t')
    print('\nprog:', repr(prog), sep='\t', file=sys.stderr)


def run_command_conf(prog=None, args=None):
    from argparse import ArgumentParser
    from volkanic.system import CommandConf
    desc = 'volkanic command-conf runner'
    parser = ArgumentParser(prog=prog, description=desc)
    parser.add_argument('path', help='a YAML file')
    parser.add_argument(
        'subcmd', nargs='?', default='default',
        help='a sub command',
    )
    ns = parser.parse_args(args=args)
    CommandConf.from_yaml(ns.path)(ns.subcmd)


registry = _CReg({
    'volkanic.default': 'argv',
    'volkanic.default:run_command_conf': 'runconf'
})
