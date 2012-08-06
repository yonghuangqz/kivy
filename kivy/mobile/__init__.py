'''
mobile providers
================

'''

from kivy.utils import platform as core_platform
from kivy.logger import Logger

plateform = core_platform()

if plateform == 'android':
    try:
        import kivy.mobile.providers.android_vibrate.Android_VibrateProvider as Vibrator
    except:
        err = 'Unable to import vibrate, does the app have the right permissions?'
        Logger.warning(err)

    try:
        import kivy.mobile.providers.android_accelerometer.Android_AccelerometerProvider as Accelerometer
    except:
        err = 'Unable to import android accelerator'
        Logger.warning(err)


if __name__ == '__main__':
    Vibrator().vibrate()
    Accelerometer().read()
