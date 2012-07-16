"""
This module intend to provide access to various device status values, if
availables, on handled device
"""

try:
    import android
    family = 'android'

except:
    try:
        import ios
        family = 'ios'
    except:
        raise NotImplementedError('This plateform is not supported as a mobile plateform')
