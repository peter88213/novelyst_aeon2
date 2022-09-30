""" Build an aeon2yw  novelyst plugin.
        
In order to distribute a single script without dependencies, 
this script "inlines" all modules imported from the pywriter package.

The PyWriter project (see see https://github.com/peter88213/PyWriter)
must be located on the same directory level as the aeon2yw project. 

For further information see https://github.com/peter88213/aeon2yw_novelyst
Published under the MIT License (https://opensource.org/licenses/mit-license.php)
"""
import os
import sys
sys.path.insert(0, f'{os.getcwd()}/../../PyWriter/src')
import inliner

SRC = '../src/'
BUILD = '../test/'
SOURCE_FILE = f'{SRC}aeon2yw_novelyst.py'
TARGET_FILE = f'{BUILD}aeon2yw_novelyst.py'


def main():
    inliner.run(SOURCE_FILE, TARGET_FILE, 'aeon2ywlib', '../../aeon2yw/src/')
    inliner.run(TARGET_FILE, TARGET_FILE, 'pywriter', '../../PyWriter/src/')
    print('Done.')


if __name__ == '__main__':
    main()
