"""
This module intend to provide access to accelerometer, if availables, on
handled device
"""


class AccelerometerProvider(object):
    def __init__(self, **kwargs):
        raise NotImplementedError

    def vibrate(self, duration=1):
        raise NotImplementedError
