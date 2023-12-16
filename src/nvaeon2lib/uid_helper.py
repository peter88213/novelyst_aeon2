"""Provide a GUID generator for Aeon Timeline 2.

Copyright (c) 2024 Peter Triesberger
For further information see https://github.com/peter88213/aeon2nv
License: GNU GPLv3 (https://www.gnu.org/licenses/gpl-3.0.en.html)
"""
from hashlib import pbkdf2_hmac

guidChars = list('ABCDEF0123456789')


def get_sub_guid(key, size):
    """Return a string generated from a bytes key.
    
    Positional arguments:
        key: bytes -- key.
        size: int -- length of the returned string.
    """
    keyInt = int.from_bytes(key, byteorder='big')
    guid = ''
    while len(guid) < size and keyInt > 0:
        guid += guidChars[keyInt % len(guidChars)]
        keyInt //= len(guidChars)
    return guid


def get_uid(text):
    """Return a GUID for Aeon Timeline.
    
    Positional arguments:
        text -- string to generate a GUID from.

    GUID format: aaaaaaaa-bbbb-cccc-dddd-eeeeeeeeeeee
    """
    text = text.encode('utf-8')
    sizes = [8, 4, 4, 4, 12]
    salts = [b'a', b'b', b'c', b'd', b'e']
    guid = []
    for i in range(5):
        key = pbkdf2_hmac('sha1', text, salts[i], 1)
        guid.append(get_sub_guid(key, sizes[i]))
    return '-'.join(guid)
