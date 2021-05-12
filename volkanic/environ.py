#!/usr/bin/env python3
# coding: utf-8

import importlib
import logging
import os
import re
import sys
import weakref

import json5

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


def _abs_path_join(*paths):
    path = os.path.join(*paths)
    return os.path.abspath(path)


class _GIMeta(SingletonMeta):
    def __new__(mcs, name, bases, attrs):
        pn = attrs.get('package_name')
        if not pn:
            msg = '{}.package_name is missing'.format(name)
            raise ValueError(msg)
        if not re.match(r'\w[\w.]*\w', pn):
            msg = 'invalid {}.package_name: "{}"'.format(name, pn)
            raise ValueError(msg)
        return super().__new__(mcs, name, bases, attrs)


class GlobalInterface(metaclass=_GIMeta):
    # for package dir, [a-z.]+
    package_name = 'volkanic'

    # for project dir locating (under_project_dir())
    project_source_depth = 0

    # default config and log format
    default_config = {}
    default_logfmt = \
        '%(asctime)s %(levelname)s [%(process)s,%(thread)s] %(name)s %(message)s'

    @cached_property
    def project_name(self):
        return self.package_name.replace('.', '-')

    @cached_property
    def identifier(self):
        # for envvar prefix and default conf paths, [a-z]+
        return self.package_name.replace('.', '_')

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
        if path:
            msg = '{}.conf, path'.format(self.__class__.__name__)
            print(msg, path, file=sys.stderr)
            user_config = self._parse_conf(path)
        else:
            user_config = {}
        config = dict(self.default_config)
        config.update(user_config)
        return config

    @staticmethod
    def under_home_dir(*paths):
        if sys.platform == 'win32':
            homedir = os.environ["HOMEPATH"]
        else:
            homedir = os.path.expanduser('~')
        return _abs_path_join(homedir, *paths)

    @classmethod
    def under_package_dir(cls, *paths) -> str:
        mod = importlib.import_module(cls.package_name)
        pkg_dir = os.path.split(mod.__file__)[0]
        if not paths:
            return pkg_dir
        return _abs_path_join(pkg_dir, *paths)

    @classmethod
    def under_project_dir(cls, *paths):
        pkg_dir = cls.under_package_dir()
        if re.search(r'[/\\](site|dist)-packages[/\\]', pkg_dir):
            return
        n = cls.project_source_depth
        n += len(cls.package_name.split('.'))
        paths = ['..'] * n + list(paths)
        return os.path.join(pkg_dir, *paths)

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
