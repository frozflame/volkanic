#!/usr/bin/env python3
# coding: utf-8
from __future__ import annotations

from volkanic.introspect import ErrorBase


class KnownError(ErrorBase):
    code = 1


class BusinessError(KnownError):
    code = 1


class TechnicalError(KnownError):
    code = 2

    def __str__(self):
        s = super().__str__()
        return f'{s} <{self.error_key}>'


class UnknownError(ErrorBase):
    code = 3


C1Error = BusinessError
C2Error = TechnicalError
C3Error = UnknownError

__all__ = [
    'KnownError',
    'BusinessError',
    'TechnicalError',
    'UnknownError',
    'C1Error',
    'C2Error',
    'C3Error',
]
