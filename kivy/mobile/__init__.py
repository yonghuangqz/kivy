# pylint: disable=W0611
'''
mobile providers
================

'''

#import os
from kivy.utils import platform as core_platform
from kivy.logger import Logger

plateform = core_platform()

if plateform == 'android':
    try:
        import kivy.mobile.providers.android_vibrate
    except:
        err = 'Unable to import android vibrate, does the app have the right permissions?'
        Logger.warning(err)
