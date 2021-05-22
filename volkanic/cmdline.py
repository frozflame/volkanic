#!/usr/bin/env python3
# coding: utf-8

import os
import sys

from volkanic.utils import load_symbol


class CommandRegistry(object):
    def __init__(self, commands, prog=''):
        self.commands = commands
        self.default_prog = prog

    @classmethod
    def from_cmddef(cls, cmddef, prog=''):
        commands = {}
        for line in cmddef.splitlines():
            line = line.strip()
            if not line:
                continue
            cmd, dotpath = line.split()[:2]
            commands[cmd] = dotpath
        return cls(commands, prog)

    @classmethod
    def from_entries(cls, entries, prog=''):
        return cls({v: k for k, v in entries.items()}, prog)

    def show_commands(self, prog):
        indent = ' ' * 4
        lines = ['available commands:', '']
        for cmd in sorted(self.commands):
            lines.append(indent + ' '.join([prog, cmd]))
        print(*lines, sep='\n', end='\n\n')

    def get_real_prog(self, argv):
        if not argv:
            return self.default_prog or '<prog>'
        if argv[0].endswith('.py'):
            return self.default_prog or argv[0]
        return os.path.basename(argv[0])

    def __call__(self, argv=None):
        argv = sys.argv if argv is None else list(argv)
        real_prog = self.get_real_prog(argv)
        try:
            dotpath = self.commands[argv[1]]
        except LookupError:
            self.show_commands(real_prog)
            sys.exit(1)

        # intended use: argparse.ArgumentParser(prog=prog)
        prog = '{} {}'.format(real_prog, argv[1])

        if ':' not in dotpath:
            dotpath += ':run'
        return load_symbol(dotpath)(prog, argv[2:])