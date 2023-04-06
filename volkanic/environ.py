#!/usr/bin/env python3
# coding: utf-8

import logging
import os
import re
import weakref
from pathlib import Path
from typing import Union

from volkanic import utils
from volkanic.compat import cached_property

_logger = logging.getLogger(__name__)


# add this in 0.6.0 -- py >= 3.6
# PathType = Union[str, os.PathLike]


class SingletonMeta(type):
    registered_instances = {}

    def __call__(cls, *args, **kwargs):
        try:
            return cls.registered_instances[cls]
        except KeyError:
            obj = super().__call__(*args, **kwargs)
            return cls.registered_instances.setdefault(cls, obj)


class WeakSingletonMeta(SingletonMeta):
    registered_instances = weakref.WeakValueDictionary()


class Singleton(metaclass=SingletonMeta):
    pass


class WeakSingleton(metaclass=WeakSingletonMeta):
    pass


class _GIMeta(SingletonMeta):
    def __new__(mcs, name, bases, attrs):
        pn = attrs.get('package_name')
        if pn is None:
            msg = '{}.package_name is missing'.format(name)
            raise ValueError(msg)
        if not isinstance(pn, str):
            msg = '{}.package_name is of wrong type'.format(name)
            raise TypeError(msg)
        if not re.match(r'\w[\w.]*\w$', pn):
            msg = 'invalid {}.package_name: "{}"'.format(name, pn)
            raise ValueError(msg)
        attrs['_classcache'] = {}
        attrs['_namespaces'] = re.split(r'[._]+', pn)
        return super().__new__(mcs, name, bases, attrs)


class _GINamespaces:
    def __get__(self, _, owner: _GIMeta) -> list:
        return getattr(owner, '_namespaces')


class _GIName:
    __slots__ = ['sep']

    def __init__(self, sep: str):
        self.sep = sep

    def __get__(self, _, owner: _GIMeta) -> Union[str, list]:
        return self.sep.join(getattr(owner, '_namespaces'))


class _GIPath:
    __slots__ = ['func', 'name']

    def __init__(self, clsmethod: classmethod):
        self.func = clsmethod.__func__

    def __set_name__(self, owner, name):
        self.name = name

    def __get__(self, _, owner: _GIMeta) -> Path:
        classcache = getattr(owner, '_classcache')
        if self.name not in classcache:
            classcache[self.name] = Path(self.func(owner))
        return classcache[self.name]


class GlobalInterface(metaclass=_GIMeta):
    # python dot-deliminated path, [a-z.]+
    package_name = 'volkanic'

    # for path and url
    # '[._]+' in package_name replaced by hyphen '-'
    project_name = _GIName('-')

    # for symbols in code
    # '[._]+' in package_name replaced by underscore '_'
    identifier = _GIName('_')

    # split package_name with '[._]+'
    namespaces = _GINamespaces()

    _options = {
        # for project dir locating (under_project_dir())
        'project_source_depth': 0,
        # for config file locating (_get_conf_paths())
        'confpath_filename': 'config.json5',
    }

    # default config and log format
    default_config = {
        '_jinja2_env': {},
    }
    default_logfmt = \
        '%(asctime)s %(levelname)s [%(process)s,%(thread)s] %(name)s %(message)s'

    @classmethod
    def _fmt_envvar_name(cls, name):
        return '{}_{}'.format(cls.identifier, name).upper()

    @classmethod
    def _get_option(cls, key: str):
        for c in cls.mro():
            options = c.__dict__.get('_options')
            try:
                return options[key]
            except (KeyError, TypeError):
                pass

    @classmethod
    def _fmt_name(cls, sep='-') -> str:
        return sep.join(cls.namespaces)

    @classmethod
    def _get_conf_path_names(cls) -> list:
        return [cls.project_name, cls._get_option('confpath_filename')]

    @classmethod
    def _get_conf_paths(cls) -> list:
        """
        Make sure this method can be called without arguments.
        Override this method in your subclasses for your specific project.
        """
        envvar_name = cls._fmt_envvar_name('confpath')
        names = cls._get_conf_path_names()
        relative_path = os.path.join(*names)
        return [
            os.environ.get(envvar_name),
            cls.under_project_dir(names[-1]),
            utils.under_home_dir_hidden(relative_path),
            os.path.join('/etc', relative_path),
            os.path.join('/', relative_path),
        ]

    @classmethod
    def _locate_conf(cls):
        """
        Returns: (str) absolute path to config file
        """
        func = getattr(cls, '_get_conf_search_paths', None)
        if func is None:
            func = cls._get_conf_paths
        paths = func()
        for path in paths:
            if not path:
                continue
            if os.path.exists(path):
                return os.path.abspath(path)

    @staticmethod
    def _parse_conf(path: str) -> dict:
        return utils.load_json5_file(path)

    @staticmethod
    def _check_conf(config: dict) -> dict:
        return config

    @cached_property
    def conf(self) -> dict:
        path = self._locate_conf()
        cn = self.__class__.__name__
        if path:
            config = self._parse_conf(path)
            utils.printerr('{}.conf, path'.format(cn), path)
        else:
            config = {}
            utils.printerr('{}.conf, hard-coded'.format(cn))
        config = utils.merge_dicts(self.default_config, config)
        return self._check_conf(config)

    @staticmethod
    def under_home_dir(*paths):
        return utils.under_home_dir(*paths)

    @classmethod
    def under_package_dir(cls, *paths) -> str:
        return utils.under_package_dir(cls.package_name, *paths)

    @classmethod
    def under_project_dir(cls, *paths):
        pkg_dir = cls.under_package_dir()
        if re.search(r'[/\\](site|dist)-packages[/\\]', pkg_dir):
            return
        n = cls._get_option('project_source_depth')
        n += len(cls.package_name.split('.'))
        paths = ['..'] * n + list(paths)
        return utils.abs_path_join(pkg_dir, *paths)

    # noinspection PyTypeChecker
    package_dir = _GIPath(under_package_dir)
    # noinspection PyTypeChecker
    project_dir = _GIPath(under_project_dir)

    @classmethod
    def _get_self(cls):
        mcs = cls.__class__
        try:
            return mcs.registered_instances[cls]
        except KeyError:
            pass

    @classmethod
    def debug(cls) -> dict:
        try:
            conf = cls._get_self().__dict__['conf']
        except (AttributeError, KeyError):
            conf = None
        mcs = cls.__class__
        return {
            'identifier': cls.identifier,
            'package_name': cls.package_name,
            'project_name': cls.project_name,
            'project_dir': cls.under_project_dir(),
            'package_dir': cls.under_package_dir(),
            'registered_instances': mcs.registered_instances,
            'conf_paths': cls._get_conf_paths(),
            'conf_path': cls._locate_conf(),
            'conf': conf,
        }

    @classmethod
    def setup_logging(cls, level=None, fmt=None):
        if not level:
            envvar_name = cls._fmt_envvar_name('loglevel')
            level = os.environ.get(envvar_name, 'DEBUG')
        fmt = fmt or cls.default_logfmt
        logging.basicConfig(level=level, format=fmt)


class GlobalInterfaceTribal(GlobalInterface):
    package_name = 'volkanic'

    def _under_data_dir(self, conf_key, *paths, mkdirs=False) -> str:
        dirpath = self.conf[conf_key]
        if not mkdirs:
            return utils.abs_path_join(dirpath, *paths)
        return utils.abs_path_join_and_mkdirs(dirpath, *paths)

    def under_data_dir(self, *paths, mkdirs=False) -> str:
        return self._under_data_dir('data_dir', *paths, mkdirs=mkdirs)

    def _under_resources_dir(self, conf_key, default, *paths) -> str:
        dirpath = self.conf.get(conf_key)
        if not dirpath:
            dirpath = self.under_project_dir(default)
        if not dirpath or not os.path.isdir(dirpath):
            raise NotADirectoryError(dirpath)
        return utils.abs_path_join(dirpath, *paths)

    def under_resources_dir(self, *paths) -> str:
        f = self._under_resources_dir
        return f('resources_dir', 'resources', *paths)

    def under_temp_dir(self, ext=''):
        name = os.urandom(17).hex() + ext
        return self.under_data_dir('tmp', name, mkdirs=True)


GlobalInterfaceTrial = GlobalInterfaceTribal
