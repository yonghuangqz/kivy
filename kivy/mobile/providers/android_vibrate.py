'''
Support of Android Vibrate function
===================================

'''

__all__ = ('Android_VibrateProvider', )

from kivy.mobile.Vibrator import VibratorProvider


class Android_VibrateProvider(VibratorProvider):
    '''Android Vibrate implementation'''

    def __init__(self, **kwargs):
        pass

    def vibrate(self, duration=1, intensity=1):
        pass
