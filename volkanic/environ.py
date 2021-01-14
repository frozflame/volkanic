#!/usr/bin/env python3
# coding: utf-8

import copy
import os
from functools import cached_property
import re
import logging

import yaml


logger = logging.getLogger(__name__)


class Singleton(object):
    registered_instances = {}

    def __new__(cls, *args, **kwargs):
        if cls not in cls.registered_instances:
            obj = super(Singleton, cls).__new__(cls, *args, **kwargs)
            cls.registered_instances[cls] = obj
        return cls.registered_instances[cls]


_logfmt = '%(asctime)s %(levelname)s [%(process)s,%(thread)s] %(name)s %(message)s'


class GlobalInterface(Singleton):
    # default config and log format
    _config = {}
    _logfmt = _logfmt

    # envvar prefix and conf paths will depend on this
    package_name = 'volkanic'

    @classmethod
    def _fmt_envvar_name(cls, name):
        prefix = cls.package_name.replace('.', '')
        return '{}_{}'.format(prefix, name).upper()

    @classmethod
    def _locate_conf(cls):
        """\
        Get path to the config file.
        (Override this method in your subclasses for your specific project.)
        Returns: (str) absolute path to config file
        """
        envvar_name = cls._fmt_envvar_name('confpath')
        path = os.environ.get(envvar_name)
        if path:
            return path
        name = cls.package_name.replace('.', '-')
        paths = [
            '/{}/config.yml'.format(name),
            os.path.expanduser('~/.{}/config.yml'.format(name)),
            cls.under_package_dir('../../config.yml'),
        ]
        for path in paths:
            path = os.path.abspath(path)
            if os.path.exists(path):
                return path

    @cached_property
    def conf(self) -> dict:
        path = self._locate_conf()
        if path:
            user_config = yaml.safe_load(open(path))
            logger.info('GlobalInterface.conf, path %s', path)
        else:
            user_config = {}
        config = dict(self._config)
        config.update(user_config)
        for k in ['data_dir', 'resources_dir']:
            config[k] = os.path.expanduser(config[k])
        return config

    def under_data_dir(self, *paths) -> str:
        dirpath = self.conf['data_dir']
        return os.path.join(dirpath, *paths)

    @classmethod
    def under_package_dir(cls, *paths) -> str:
        mod = importlib.import_module(cls.package_name)
        pkg_dir = os.path.split(mod.__file__)[0]
        if not paths:
            return pkg_dir
        return os.path.join(pkg_dir, *paths)

    def under_resources_dir(self, *paths):
        dirpath = self.conf['resources_dir']
        return os.path.join(dirpath, *paths)

    @cached_property
    def jinja2_env(self):
        from jinja2 import Environment, PackageLoader, select_autoescape
        return Environment(
            loader=PackageLoader(self.package_name, 'templates'),
            autoescape=select_autoescape(['html', 'xml'])
        )

    @classmethod
    def setup_logging(cls, level=None):
        if not level:
            envvar_name = cls._fmt_envvar_name('loglevel')
            level = os.environ.get(envvar_name, 'DEBUG')
        logging.basicConfig(level=level, format=cls._logfmt)
