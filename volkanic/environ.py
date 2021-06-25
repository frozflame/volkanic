#!/usr/bin/env python3
# coding: utf-8

import importlib
import logging
import os
import re
import sys
import weakref

import json5

from volkanic import utils
from volkanic.compat import cached_property

logger = logging.getLogger(__name__)


class Singleton(object):
    registered_instances = {}

    def __new__(cls, *args, **kwargs):
        try:
            return cls.registered_instances[cls]
        except KeyError:
            obj = super(Singleton, cls).__new__(cls, *args, **kwargs)
            return cls.registered_instances.setdefault(cls, obj)


class WeakSingleton(object):
    registered_instances = weakref.WeakValueDictionary()


class SingletonMeta(type):
    registered_instances = {}

    def __call__(cls, *args, **kwargs):
        try:
            return cls.registered_instances[cls]
        except KeyError:
            obj = super().__call__(*args, **kwargs)
            return cls.registered_instances.setdefault(cls, obj)


class _GIMeta(SingletonMeta):
    def __new__(mcs, name, bases, attrs):
        pn = attrs.get('package_name')
        if not isinstance(pn, str):
            msg = '{}.package_name is of wrong type'.format(name)
            raise TypeError(msg)
        if not pn:
            msg = '{}.package_name is missing'.format(name)
            raise ValueError(msg)
        if not re.match(r'\w[\w.]*\w', pn):
            msg = 'invalid {}.package_name: "{}"'.format(name, pn)
            raise ValueError(msg)
        return super().__new__(mcs, name, bases, attrs)


class _PackageNameDerivant:
    __slots__ = ['_replacement']

    def __init__(self, replacement):
        self._replacement = replacement

    def __get__(self, _, owner):
        return owner.package_name.replace('.', self._replacement)


class GlobalInterface(metaclass=_GIMeta):
    # python dot-deliminated path, [a-z.]+
    package_name = 'volkanic'

    # for path and url
    # dot '.' in package_name replaced by hyphen '-'
    project_name = _PackageNameDerivant('-')

    # for symbols in code
    # dot '.' in package_name replaced by underscore '_'
    identifier = _PackageNameDerivant('_')

    # for project dir locating (under_project_dir())
    project_source_depth = 0

    # default config and log format
    default_config = {}
    default_logfmt = \
        '%(asctime)s %(levelname)s [%(process)s,%(thread)s] %(name)s %(message)s'

    @classmethod
    def _fmt_envvar_name(cls, name):
        return '{}_{}'.format(cls.identifier, name).upper()

    @classmethod
    def _get_conf_search_paths(cls):
        """
        Make sure this method can be called without arguments.
        Override this method in your subclasses for your specific project.
        """
        envvar_name = cls._fmt_envvar_name('confpath')
        pn = cls.project_name
        return [
            os.environ.get(envvar_name),
            cls.under_project_dir('config.json5'),
            cls.under_home_dir('.{}/config.json5'.format(pn)),
            '/etc/{}/config.json5'.format(pn),
            '/{}/config.json5'.format(pn),
        ]

    @classmethod
    def _locate_conf(cls):
        """
        Returns: (str) absolute path to config file
        """
        for path in cls._get_conf_search_paths():
            if not path:
                continue
            if os.path.exists(path):
                return os.path.abspath(path)

    @staticmethod
    def _parse_conf(path: str):
        return json5.load(open(path))

    @cached_property
    def conf(self) -> dict:
        path = self._locate_conf()
        cn = self.__class__.__name__
        if path:
            config = self._parse_conf(path)
            print('{}.conf, path'.format(cn), path, file=sys.stderr)
        else:
            config = {}
            print('{}.conf, hard-coded'.format(cn), file=sys.stderr)
        return utils.merge_dicts(self.default_config, config)

    @staticmethod
    def under_home_dir(*paths):
        if sys.platform == 'win32':
            homedir = os.environ["HOMEPATH"]
        else:
            homedir = os.path.expanduser('~')
        return utils.abs_path_join(homedir, *paths)

    @classmethod
    def under_package_dir(cls, *paths) -> str:
        mod = importlib.import_module(cls.package_name)
        pkg_dir = os.path.split(mod.__file__)[0]
        if not paths:
            return pkg_dir
        return utils.abs_path_join(pkg_dir, *paths)

    @classmethod
    def under_project_dir(cls, *paths):
        pkg_dir = cls.under_package_dir()
        if re.search(r'[/\\](site|dist)-packages[/\\]', pkg_dir):
            return
        n = cls.project_source_depth
        n += len(cls.package_name.split('.'))
        paths = ['..'] * n + list(paths)
        return utils.abs_path_join(pkg_dir, *paths)

    @cached_property
    def jinja2_env(self):
        # noinspection PyPackageRequirements
        from jinja2 import Environment, PackageLoader, select_autoescape
        return Environment(
            loader=PackageLoader(self.package_name, 'templates'),
            autoescape=select_autoescape(['html', 'xml'])
        )

    @classmethod
    def setup_logging(cls, level=None, fmt=None):
        if not level:
            envvar_name = cls._fmt_envvar_name('loglevel')
            level = os.environ.get(envvar_name, 'DEBUG')
        fmt = fmt or cls.default_logfmt
        logging.basicConfig(level=level, format=fmt)
