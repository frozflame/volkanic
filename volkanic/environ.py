#!/usr/bin/env python3
# coding: utf-8

import importlib
import logging
import os
import sys
from functools import cached_property

import json5

logger = logging.getLogger(__name__)


class Singleton(object):
    registered_instances = {}

    def __new__(cls, *args, **kwargs):
        if cls not in cls.registered_instances:
            obj = super(Singleton, cls).__new__(cls, *args, **kwargs)
            cls.registered_instances[cls] = obj
        return cls.registered_instances[cls]


def _path_join(*paths):
    path = os.path.join(*paths)
    return os.path.abspath(path)


class GlobalInterface(Singleton):
    # for envvar prefix and default conf paths, [a-z]+
    primary_name = 'volcanic'

    # for package dir, [a-z.]+
    package_name = 'volkanic'

    meta_config = {
        'src_depth': 0,
        'filename': 'config.json5',
    }

    # default config and log format
    default_config = {}
    default_logfmt = \
        '%(asctime)s %(levelname)s [%(process)s,%(thread)s] %(name)s %(message)s'

    @classmethod
    def _fmt_envvar_name(cls, name):
        return '{}_{}'.format(cls.primary_name, name).upper()

    @classmethod
    def _get_conf_search_paths(cls):
        """
        Make sure this method can be called without arguments.
        """
        filename = cls.meta_config['filename']
        tmpls = [
            '/etc/{}/{}',
            '/{}/{}',
            '/data/local/{}/{}',
            '/data/{}/{}',
            os.path.expanduser('~/.{}/{}'),
        ]
        paths = [p.format(cls.primary_name, filename) for p in tmpls]
        paths += [cls.under_project_dir(filename)]
        return paths

    @classmethod
    def _locate_conf(cls):
        """
        Returns: (str) absolute path to config file
        """
        envvar_name = cls._fmt_envvar_name('confpath')
        try:
            return os.environ[envvar_name]
        except KeyError:
            pass
        for path in cls._get_conf_search_paths():
            path = os.path.abspath(path)
            if os.path.exists(path):
                return path

    @staticmethod
    def _parse_conf(path: str):
        return json5.load(open(path))

    @cached_property
    def conf(self) -> dict:
        path = self._locate_conf()
        if path:
            print('GlobalInterface.conf, path', path, file=sys.stderr)
            user_config = self._parse_conf(path)
        else:
            user_config = {}
        config = dict(self.default_config)
        config.update(user_config)
        return config

    def under_data_dir(self, *paths) -> str:
        dirpath = self.conf['data_dir']
        path = os.path.join(dirpath, *paths)
        return os.path.abspath(path)

    @classmethod
    def under_package_dir(cls, *paths) -> str:
        mod = importlib.import_module(cls.package_name)
        pkg_dir = os.path.split(mod.__file__)[0]
        if not paths:
            return pkg_dir
        path = os.path.join(pkg_dir, *paths)
        return os.path.abspath(path)

    def under_resources_dir(self, *paths):
        dirpath = self.conf['resources_dir']
        return os.path.join(dirpath, *paths)

    @classmethod
    def under_project_dir(cls, *paths):
        n = cls.meta_config.get('src_depth', 0)
        n += len(cls.package_name.split())
        paths = ['..'] * n + list(paths)
        return cls.under_package_dir(*paths)

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
