'''
Support of Android Vibrate function
===================================

'''

__all__ = ('Android_VibrateProvider', )

from kivy.mobile.vibrator import VibratorProvider
import android


class Android_VibrateProvider(VibratorProvider):
    '''Android Vibrate implementation'''

    def __init__(self, **kwargs):
        pass

    def vibrate(self, duration=1):
        android.vibrate(duration)
        pass
