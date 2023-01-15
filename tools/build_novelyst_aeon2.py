""" Build an aeon2yw  novelyst plugin.
        
In order to distribute a single script without dependencies, 
this script "inlines" all modules imported from the pywriter package.

The PyWriter project (see see https://github.com/peter88213/PyWriter)
must be located on the same directory level as the aeon2yw project. 

For further information see https://github.com/peter88213/novelyst_aeon2
License: GNU GPLv3 (https://www.gnu.org/licenses/gpl-3.0.en.html)
"""
import os
import sys
sys.path.insert(0, f'{os.getcwd()}/../../PyWriter/src')
import inliner

SRC = '../src/'
BUILD = '../test/'
SOURCE_FILE = f'{SRC}novelyst_aeon2.py'
TARGET_FILE = f'{BUILD}novelyst_aeon2.py'


def main():
    inliner.run(SOURCE_FILE, TARGET_FILE, 'aeon2ywlib', '../../aeon2yw/src/')
    inliner.run(TARGET_FILE, TARGET_FILE, 'pywriter', '../../PyWriter/src/')
    print('Done.')


if __name__ == '__main__':
    main()
