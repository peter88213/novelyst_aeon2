"""Provide helper scripts to calculate the moon phase for Aeon Timeline 2 events.

Copyright (c) 2022 Peter Triesberger
For further information see https://github.com/peter88213/aeon2yw
License: GNU GPLv3 (https://www.gnu.org/licenses/gpl-3.0.en.html)
"""
import sys
import math


def get_moon_phase(dateStr):
    """Return a single value - the phase day (0 to 29, where 0=new moon, 15=full etc.) 
    for the selected date.
    Date format is 'yyyy-mm-dd'.
    This is based on a 'do it in your head' algorithm by John Conway. 
    In its current form, it's only valid for the 20th and 21st centuries.
    See: http://www.ben-daglish.net/moon.shtml
    """
    try:
        y, m, d = dateStr.split('-')
        year = int(y)
        month = int(m)
        day = int(d)
        r = year % 100
        r %= 19
        if r > 9:
            r -= 19
        r = ((r * 11) % 30) + month + day
        if month < 3:
            r += 2
        if year < 2000:
            r -= 4
        else:
            r -= 8.3
        r = math.floor(r + 0.5) % 30
        if r < 0:
            r += 30
    except:
        r = None
    return r


def get_moon_phase_plus(dateStr):
    """Return a string containing the moon phase plus a pseudo-graphic display.
    """
    s = '  ))))))))))))OOO(((((((((((( '
    p = '00¼¼¼¼½½½½¾¾¾¾111¾¾¾¾½½½½¼¼¼¼0'
    r = get_moon_phase(dateStr)
    if r is not None:
        result = f'{r} [  {s[r]}  ] {p[r]}'
    else:
        result = ''
    return result


if __name__ == '__main__':
    print(get_moon_phase(sys.argv[1]))
