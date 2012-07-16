"""
This module intend to provide access to accelerator values, if availables, on
handled device
"""
from kivy.modile.device import family


def get_func(name):
    return locals()['_' + family + name]


def _android_read_accelerator():
    raise NotImplementedError


def _ios_read_accelerator():
    raise NotImplementedError


read_accelerator = get_func('read_accelerator')
