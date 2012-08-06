"""
This module intend to provide access to vibrator, if availables, on handled
device
"""


class VibrateProvider(object):
    "Vibrator Provider interface"

    def __init__(self, **kwargs):
        raise NotImplementedError

    def vibrate(self, duration=1):
        raise NotImplementedError
