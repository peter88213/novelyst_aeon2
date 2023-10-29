"""Provide helper functions for Aeon Timeline 2 file operation.

Copyright (c) 2022 Peter Triesberger
For further information see https://github.com/peter88213/aeon2nv
License: GNU GPLv3 (https://www.gnu.org/licenses/gpl-3.0.en.html)
"""
import zipfile
import codecs
import json
import os
from novxlib.novx_globals import *
from json import JSONDecodeError


def open_timeline(filePath):
    """Unzip the project file and read 'timeline.json'.

    Positional arguments:
        filePath -- Path of the .aeon project file to read.
        
    Return a Python object containing the timeline structure.
    Raise the "Error" exception in case of error. 
    """
    try:
        with zipfile.ZipFile(filePath, 'r') as myzip:
            jsonBytes = myzip.read('timeline.json')
            jsonStr = codecs.decode(jsonBytes, encoding='utf-8')
    except:
        raise Error(f'{_("Cannot read timeline data")}.')
    if not jsonStr:
        raise Error(f'{_("No JSON part found in timeline data")}.')
    try:
        jsonData = json.loads(jsonStr)
    except JSONDecodeError:
        raise Error(f'{_("Invalid JSON data in timeline")}.')
    return jsonData


def save_timeline(jsonData, filePath):
    """Write the timeline to a zipfile located at filePath.
    
    Positional arguments:
        jsonData -- Python object containing the timeline structure.
        filePath -- Path of the .aeon project file to write.
        
    Raise the "Error" exception in case of error. 
    """
    backedUp = False
    if os.path.isfile(filePath):
        try:
            os.replace(filePath, f'{filePath}.bak')
        except:
            raise Error(f'{_("Cannot overwrite file")}: "{norm_path(filePath)}".')
        else:
            backedUp = True
    try:
        with zipfile.ZipFile(filePath, 'w', compression=zipfile.ZIP_DEFLATED) as f:
            f.writestr('timeline.json', json.dumps(jsonData))
    except:
        if backedUp:
            os.replace(f'{filePath}.bak', filePath)
        raise Error(f'{_("Cannot write file")}: "{norm_path(filePath)}".')

