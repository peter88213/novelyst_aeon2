"""Aeon Timeline 2 sync plugin for novelyst.

Version @release
Compatibility: novelyst v2.0 API 
Requires Python 3.6+
Copyright (c) 2022 Peter Triesberger
For further information see https://github.com/peter88213/novelyst_aeon2
License: GNU GPLv3 (https://www.gnu.org/licenses/gpl-3.0.en.html)
"""
import os
import sys
from pathlib import Path
import tkinter as tk
import locale
import gettext
from tkinter import messagebox
from datetime import datetime
from pywriter.pywriter_globals import *
from pywriter.config.configuration import Configuration
from pywriter.file.doc_open import open_document
from aeon2ywlib.json_timeline2 import JsonTimeline2
from aeon2ywlib.yw7_target import Yw7Target

# Initialize localization.
LOCALE_PATH = f'{os.path.dirname(sys.argv[0])}/locale/'
CURRENT_LANGUAGE = locale.getlocale()[0][:2]
try:
    t = gettext.translation('novelyst_aeon2', LOCALE_PATH, languages=[CURRENT_LANGUAGE])
    _ = t.gettext
except:

    def _(message):
        return message

APPLICATION = 'Aeon Timeline 2'
PLUGIN = f'{APPLICATION} plugin v@release'
INI_FILENAME = 'aeon2yw.ini'
INI_FILEPATH = '.pywriter/aeon2yw/config'


class Plugin():
    """Plugin class for synchronization with Aeon Timeline 2.
    
    Public methods:
        disable_menu() -- disable menu entries when no project is open.
        enable_menu() -- enable menu entries when a project is open.
        
    """
    VERSION = '@release'
    NOVELYST_API = '2.0'
    DESCRIPTION = 'Synchronize with Aeon Timeline 2'
    URL = 'https://peter88213.github.io/novelyst_aeon2'

    SETTINGS = dict(
        narrative_arc='Narrative',
        property_description='Description',
        property_notes='Notes',
        role_location='Location',
        role_item='Item',
        role_character='Participant',
        type_character='Character',
        type_location='Location',
        type_item='Item',
        color_scene='Red',
        color_event='Yellow',
    )
    OPTIONS = dict(
        scenes_only=True,
        add_moonphase=False,
    )

    def install(self, ui):
        """Add a submenu to the main menu.
        
        Positional arguments:
            ui -- reference to the NovelystTk instance of the application.
        """
        self._ui = ui

        # Create a submenu
        self._pluginMenu = tk.Menu(self._ui.toolsMenu, tearoff=0)
        self._ui.toolsMenu.add_cascade(label=APPLICATION, menu=self._pluginMenu)
        self._ui.toolsMenu.entryconfig(APPLICATION, state='disabled')
        self._pluginMenu.add_command(label=_('Information'), command=self._info)
        self._pluginMenu.add_separator()
        # self._pluginMenu.add_command(label=_('Settings'), command=self._edit_settings)
        # self._pluginMenu.add_separator()
        self._pluginMenu.add_command(label=_('Update the timeline'), command=self._export_from_yw)
        self._pluginMenu.add_command(label=_('Update the project'), command=self._import_to_yw)
        self._pluginMenu.add_separator()
        self._pluginMenu.add_command(label=_('Add or update moon phase data'), command=self._add_moonphase)
        self._pluginMenu.add_separator()
        self._pluginMenu.add_command(label=_('Edit the timeline'), command=self._launch_application)

    def _get_config(self, sourcePath):
        """ Read persistent configuration data for Aeon 2 conversion.
        
        First, look for a global configuration file in the aeon2yw installation directory,
        then look for a local configuration file in the project directory.
        """
        sourceDir = os.path.dirname(sourcePath)
        if not sourceDir:
            sourceDir = '.'
        try:
            homeDir = str(Path.home()).replace('\\', '/')
            pluginCnfDir = f'{homeDir}/{INI_FILEPATH}'
        except:
            pluginCnfDir = '.'
        iniFiles = [f'{pluginCnfDir}/{INI_FILENAME}', f'{sourceDir}/{INI_FILENAME}']
        configuration = Configuration(self.SETTINGS, self.OPTIONS)
        for iniFile in iniFiles:
            configuration.read(iniFile)
        kwargs = {}
        kwargs.update(configuration.settings)
        kwargs.update(configuration.options)
        return kwargs

    def _edit_settings(self):
        """Toplevel window"""

    def disable_menu(self):
        """Disable menu entries when no project is open."""
        self._ui.toolsMenu.entryconfig(APPLICATION, state='disabled')

    def enable_menu(self):
        """Enable menu entries when a project is open."""
        self._ui.toolsMenu.entryconfig(APPLICATION, state='normal')

    def _launch_application(self):
        """Launch Aeon Timeline 2 with the current project."""
        if self._ui.prjFile:
            timelinePath = f'{os.path.splitext(self._ui.prjFile.filePath)[0]}{JsonTimeline2.EXTENSION}'
            if os.path.isfile(timelinePath):
                if self._ui.lock():
                    open_document(timelinePath)
            else:
                self._ui.set_info_how(_('!No {} file available for this project.').format(APPLICATION))

    def _add_moonphase(self):
        """Add/update moon phase data.
        
        Add the moon phase to the event properties.
        If the moon phase event property already exists, just update.
        """
        #--- Try to get persistent configuration data
        if self._ui.prjFile:
            timelinePath = f'{os.path.splitext(self._ui.prjFile.filePath)[0]}{JsonTimeline2.EXTENSION}'
            if os.path.isfile(timelinePath):
                sourceDir = os.path.dirname(timelinePath)
                if not sourceDir:
                    sourceDir = '.'
                try:
                    homeDir = str(Path.home()).replace('\\', '/')
                    pluginCnfDir = f'{homeDir}/{INI_FILEPATH}'
                except:
                    pluginCnfDir = '.'
                iniFiles = [f'{pluginCnfDir}/{INI_FILENAME}', f'{sourceDir}/{INI_FILENAME}']
                configuration = Configuration(self.SETTINGS, self.OPTIONS)
                for iniFile in iniFiles:
                    configuration.read(iniFile)
                kwargs = {}
                kwargs.update(configuration.settings)
                kwargs.update(configuration.options)
                kwargs['add_moonphase'] = True
                timeline = JsonTimeline2(timelinePath, **kwargs)
                try:
                    timeline.read()
                    timeline.write()
                    message = f'{_("File written")}: "{norm_path(timeline.filePath)}".'
                except Error as ex:
                    message = f'!{str(ex)}'
                self._ui.set_info_how(message)

    def _info(self):
        """Show information about the Aeon Timeline 2 file."""
        if self._ui.prjFile:
            timelinePath = f'{os.path.splitext(self._ui.prjFile.filePath)[0]}{JsonTimeline2.EXTENSION}'
            if os.path.isfile(timelinePath):
                try:
                    timestamp = os.path.getmtime(timelinePath)
                    if timestamp > self._ui.prjFile.timestamp:
                        cmp = _('newer')
                    else:
                        cmp = _('older')
                    fileDate = datetime.fromtimestamp(timestamp).replace(microsecond=0).isoformat(sep=' ')
                    message = _('{0} file is {1} than the novelyst project.\n (last saved on {2})').format(APPLICATION, cmp, fileDate)
                except:
                    message = _('Cannot determine file date.')
            else:
                message = _('No {} file available for this project.').format(APPLICATION)
            messagebox.showinfo(PLUGIN, message)

    def _export_from_yw(self):
        """Update the timeline from novelyst.
        
        Note:
        This works by merging the timeline with the open project as a source object.
        The JsonTimeline2 target object's merge method reads from the disk.
        """
        if self._ui.prjFile:
            timelinePath = f'{os.path.splitext(self._ui.prjFile.filePath)[0]}{JsonTimeline2.EXTENSION}'
            if not os.path.isfile(timelinePath):
                self._ui.set_info_how(_('!No {} file available for this project.').format(APPLICATION))
                return

            if self._ui.ask_yes_no(_('Save the project and update the timeline?')):
                self._ui.save_project()
                kwargs = self._get_config(timelinePath)
                source = self._ui.prjFile
                target = JsonTimeline2(timelinePath, **kwargs)
                try:
                    target.merge(source)
                    target.write()
                    message = f'{_("File written")}: "{norm_path(target.filePath)}".'
                except Error as ex:
                    message = f'!{str(ex)}'
                self._ui.set_info_how(message)

    def _import_to_yw(self):
        """Update the current project from the timeline.
        
        Note:
        The Yw7WorkFile object of the open project cannot be used as target object.
        This is because the JsonTimeline2 source object's IDs do not match, so 
        the scenes and other elements are identified by their titles when merging.
        This is done by the special Yw7Target object. Its merge method reads from the disk. 
        Re-reading the project afterwards is the safest way to get a display update.
        """
        if self._ui.prjFile:
            timelinePath = f'{os.path.splitext(self._ui.prjFile.filePath)[0]}{JsonTimeline2.EXTENSION}'
            if not os.path.isfile(timelinePath):
                self._ui.set_info_how(_('!No {} file available for this project.').format(APPLICATION))
                return

            if self._ui.ask_yes_no(_('Save the project and update it?')):
                self._ui.save_project()
                kwargs = self._get_config(timelinePath)
                source = JsonTimeline2(timelinePath, **kwargs)
                target = Yw7Target(self._ui.prjFile.filePath, **kwargs)
                try:
                    source.read()
                    target.merge(source)
                    target.write()
                    message = f'{_("File written")}: "{norm_path(target.filePath)}".'
                except Error as ex:
                    message = f'!{str(ex)}'

                # Reopen the project.
                self._ui.reloading = True
                # avoid popup message (novelyst v0.52+)
                self._ui.open_project(self._ui.prjFile.filePath)
                self._ui.set_info_how(message)
