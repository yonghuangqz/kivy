"""
This module intend to provide access to accelerometer values, if availables, on
handled device
"""

__all__ = ('Android_AccelerometerProvider', )

from kivy.mobile.accelerometer import AccelerometerProvider
import android


class Android_AccelerometerProvider(AccelerometerProvider):
    '''Android Vibrate implementation'''

    def __init__(self, **kwargs):
        android.accelerometer_enable(True)

    def read(self):
        android.accelerometer_reading()
