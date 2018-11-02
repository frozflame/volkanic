#!/usr/bin/env python3
# coding: utf-8

from __future__ import unicode_literals

import contextlib
import importlib
import os
import sys


@contextlib.contextmanager
def remember_cwd():
    curdir = os.getcwd()
    try:
        yield
    finally:
        os.chdir(curdir)


class CommandNotFound(KeyError):
    pass


class CommandConf(object):
    def __init__(self, commands):
        self.commands = dict(commands)
        self.module_prefix = ''

    @classmethod
    def from_yaml(cls, name, defaultdir=None):
        import yaml
        ext = os.path.splitext(name)[1].lower()
        if ext not in ['.yml', '.yaml']:
            name += '.yml'
        path = cls._locate(name, defaultdir)
        return cls(yaml.load(open(path)))

    @classmethod
    def from_json(cls, name, defaultdir=None):
        import json
        ext = os.path.splitext(name)[1].lower()
        if ext != '.json':
            name += '.json'
        path = cls._locate(name, defaultdir)
        return cls(json.load(open(path)))

    @staticmethod
    def _locate(path, defaultdir):
        paths = [path]
        if defaultdir is not None:
            paths.append(os.path.join(defaultdir, path))
        for path in paths:
            if os.path.isfile(path):
                return path
        raise FileNotFoundError(path)

    def _execute(self, params):
        modpath = params['module']
        if not modpath.startswith(self.module_prefix):
            modpath = self.module_prefix + modpath
            modpath = modpath.replace('..', '.')

        module = importlib.import_module(modpath)
        call = getattr(module, params['call'])
        args = params.get('args', [])
        if not isinstance(args, (list, tuple)):
            args = [args]
        call(*args, **params.get('kwargs', {}))
        # call(*args)

    def __call__(self, cmd):
        params = self.commands.get('_global', {}).copy()
        try:
            params.update(self.commands[cmd])
        except KeyError:
            raise CommandNotFound(str(cmd))

        with remember_cwd():
            os.chdir(params.get('cd', '.'))
            self._execute(params)


class CommandRegistry(object):
    def __init__(self, entries):
        self.entries = entries
        self.commands = {v: k for k, v in entries.items()}

    def show_commands(self):
        print('availabe commands:')
        for cmd in self.commands:
            print('-', cmd)

    def __call__(self, argv=None):
        if argv is None:
            argv = sys.argv
        else:
            argv = list(argv)

        try:
            dotpath = self.commands[argv[1]]
        except LookupError:
            self.show_commands()
            sys.exit(1)

        # intended use: argparse.ArgumentParser(prog=prog)
        prog = '{} {}'.format(os.path.basename(argv[0]), argv[1])

        if ':' not in dotpath:
            dotpath += ':run'

        dotpath, funcname = dotpath.split(':')
        mod = importlib.import_module(dotpath)
        getattr(mod, funcname)(prog, argv[2:])
