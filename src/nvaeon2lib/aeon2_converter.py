"""Provide a converter class for Aeon Timeline 2 and novelyst. 

Copyright (c) 2024 Peter Triesberger
For further information see https://github.com/peter88213/aeon2nv
License: GNU GPLv3 (https://www.gnu.org/licenses/gpl-3.0.en.html)
"""
import os

from novxlib.converter.converter import Converter
from novxlib.novx.novx_file import NovxFile
from novxlib.novx_globals import _
from novxlib.novx_globals import norm_path
from nvaeon2lib.json_timeline2 import JsonTimeline2


class Aeon2Converter(Converter):
    """A converter class for novelyst and Aeon Timeline 2."""

    def run(self, sourcePath, **kwargs):
        """Create source and target objects and run conversion.

        Positional arguments: 
            sourcePath: str -- the source file path.
        
        The direction of the conversion is determined by the source file type.
        Only novelyst project files and Aeon Timeline 2 files are accepted.
        """
        if not os.path.isfile(sourcePath):
            self.ui.set_info_how(f'!{_("File not found")}: "{norm_path(sourcePath)}".')
            return

        fileName, fileExtension = os.path.splitext(sourcePath)
        if fileExtension == JsonTimeline2.EXTENSION:
            # Source is a timeline
            sourceFile = JsonTimeline2(sourcePath, **kwargs)
            if os.path.isfile(f'{fileName}{NovxFile.EXTENSION}'):
                # Update existing novelyst project from timeline
                targetFile = NovxFile(f'{fileName}{NovxFile.EXTENSION}', **kwargs)
                self.import_to_novx(sourceFile, targetFile)
            else:
                # Create new novelyst project from timeline
                targetFile = NovxFile(f'{fileName}{NovxFile.EXTENSION}', **kwargs)
                self.create_novx(sourceFile, targetFile)
        elif fileExtension == NovxFile.EXTENSION:
            # Update existing timeline from novelyst project
            sourceFile = NovxFile(sourcePath, **kwargs)
            targetFile = JsonTimeline2(f'{fileName}{JsonTimeline2.EXTENSION}', **kwargs)
            self.export_from_novx(sourceFile, targetFile)
        else:
            # Source file format is not supported
            self.ui.set_info_how(f'!{_("File type is not supported")}: "{norm_path(sourcePath)}".')
