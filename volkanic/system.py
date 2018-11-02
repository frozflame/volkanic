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
        self.commands.setdefault('_global', {})

    @classmethod
    def from_yaml(cls, name, default_dir=None):
        import yaml
        ext = os.path.splitext(name)[1].lower()
        if ext not in ['.yml', '.yaml']:
            name += '.yml'
        path = cls._locate(name, default_dir)
        return cls(yaml.load(open(path)))

    @classmethod
    def from_json(cls, name, default_dir=None):
        import json
        ext = os.path.splitext(name)[1].lower()
        if ext != '.json':
            name += '.json'
        path = cls._locate(name, default_dir)
        return cls(json.load(open(path)))

    @staticmethod
    def _locate(path, default_dir):
        paths = [path]
        if default_dir is not None:
            paths.append(os.path.join(default_dir, path))
        for path in paths:
            if os.path.isfile(path):
                return path
        raise FileNotFoundError(path)

    @staticmethod
    def _execute(params):
        prefix = params.get('module_prefix', '')
        modpath = prefix + params['module']
        module = importlib.import_module(modpath)
        call = getattr(module, params['call'])
        args = params.get('args', [])
        if not isinstance(args, (list, tuple)):
            args = [args]
        call(*args, **params.get('kwargs', {}))

    def __call__(self, cmd):
        params = dict(self.commands['_global'])
        try:
            params.update(self.commands[cmd])
        except KeyError:
            raise CommandNotFound(str(cmd))

        with remember_cwd():
            os.chdir(params.get('cd', '.'))
            self._execute(params)

    @classmethod
    def run(cls, prog=None, args=None, default_dir=None, **kwargs):
        from argparse import ArgumentParser
        kwargs.setdefault('description', 'volkanic command-conf runner')
        parser = ArgumentParser(prog=prog, **kwargs)
        parser.add_argument('path', help='a YAML file')
        parser.add_argument(
            'subcmd', nargs='?', default='default',
            help='a sub command',
        )
        ns = parser.parse_args(args=args)
        cconf = cls.from_yaml(ns.path, default_dir)
        cconf(ns.subcmd)


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
