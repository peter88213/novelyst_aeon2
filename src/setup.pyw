#!/usr/bin/python3
"""Install the novelyst_aeon2 plugin.

Version @release

Copyright (c) 2022 Peter Triesberger
For further information see https://github.com/peter88213/novelyst_aeon2
License: GNU GPLv3 (https://www.gnu.org/licenses/gpl-3.0.en.html)
"""
import sys
import os
from shutil import copytree
from shutil import copyfile
from pathlib import Path
try:
    from tkinter import *
    from tkinter import messagebox
except ModuleNotFoundError:
    print('The tkinter module is missing. Please install the tk support package for your python3 version.')
    sys.exit(1)

APPNAME = 'aeon2yw'
PLUGIN = 'novelyst_aeon2.py'
OLD_PLUGIN = 'aeon2yw_novelyst.py'
VERSION = ' @release'
INI_FILE = f'{APPNAME}.ini'
INI_PATH = '/config/'
SAMPLE_PATH = 'sample/'
SUCCESS_MESSAGE = '''
$Appname is installed here:
$Apppath
'''

root = Tk()
processInfo = Label(root, text='')
message = []

aeon2dir = None
sampleTemplate = None


def output(text):
    message.append(text)
    processInfo.config(text=('\n').join(message))


def open_folder(installDir):
    """Open an installation folder window in the file manager.
    """
    try:
        os.startfile(os.path.normpath(installDir))
        # Windows
    except:
        try:
            os.system('xdg-open "%s"' % os.path.normpath(installDir))
            # Linux
        except:
            try:
                os.system('open "%s"' % os.path.normpath(installDir))
                # Mac
            except:
                pass


def install(pywriterPath):
    """Install the script."""
    # global aeon2dir
    # global sampleTemplate

    # Create a general PyWriter installation directory, if necessary.
    os.makedirs(pywriterPath, exist_ok=True)
    installDir = f'{pywriterPath}{APPNAME}'
    cnfDir = f'{installDir}{INI_PATH}'
    os.makedirs(cnfDir, exist_ok=True)

    # Install a configuration file, if needed.
    try:
        if not os.path.isfile(f'{cnfDir}{INI_FILE}'):
            copyfile(f'{SAMPLE_PATH}{INI_FILE}', f'{cnfDir}{INI_FILE}')
            output(f'Copying "{INI_FILE}"')
        else:
            output(f'Keeping "{INI_FILE}"')
    except:
        pass


def install_plugin(pywriterPath):
    """Install a novelyst plugin if novelyst is installed."""
    if os.path.isfile(f'./{PLUGIN}'):
        novelystDir = f'{pywriterPath}novelyst'
        pluginDir = f'{novelystDir}/plugin'
        output(f'Installing novelyst plugin at "{os.path.normpath(pluginDir)}"')
        os.makedirs(pluginDir, exist_ok=True)
        try:
            os.remove(f'{pluginDir}/{OLD_PLUGIN}')
            output('Removing old version')
        except:
            pass
        copyfile(PLUGIN, f'{pluginDir}/{PLUGIN}')
        output(f'Copying "{PLUGIN}"')
    else:
        output('Error: novelyst plugin file not found.')

    # Install the localization files.
    copytree('locale', f'{novelystDir}/locale', dirs_exist_ok=True)
    output(f'Copying "locale"')


if __name__ == '__main__':
    scriptPath = os.path.abspath(sys.argv[0])
    scriptDir = os.path.dirname(scriptPath)
    os.chdir(scriptDir)

    # Open a tk window.
    root.geometry("800x600")
    root.title(f'Install {PLUGIN}{VERSION}')
    header = Label(root, text='')
    header.pack(padx=5, pady=5)

    # Prepare the messaging area.
    processInfo.pack(padx=5, pady=5)

    # Run the installation.
    homePath = str(Path.home()).replace('\\', '/')
    pywriterPath = f'{homePath}/.pywriter/'
    novelystDir = f'{pywriterPath}novelyst'
    if os.path.isdir(novelystDir):
        try:
            install_plugin(pywriterPath)
            install(pywriterPath)
        except Exception as ex:
            output(str(ex))
    else:
        messagebox.showwarning('The novelyst applilcation seems not to be installed. please install first.')

    root.quitButton = Button(text="Quit", command=quit)
    root.quitButton.config(height=1, width=30)
    root.quitButton.pack(padx=5, pady=5)
    root.mainloop()
