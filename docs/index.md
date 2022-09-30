# aeon2yw_novelyst

## Features

### Update an existing yWriter project from a timeline

- Update scene date, time, duration, description, tags, and relationships.
- Missing scenes, characters, locations, and items are created.
- Scenes are marked "unused" if the associated event is deleted in Aeon.

### Update an existing timeline from a yWriter project

- Update event date, time, duration, description, tags, and relationships.
- Entity types "Arc", "Character", "Location", and "Item", and a *Narrative* arc are created, if missing.
- Event properties "Description" and "Notes" are created, if missing.
- Missing events, characters, locations, and items are created.
- "Narrative" events are removed if the associated scene is deleted in yWriter.

### Create a new timeline from a yWriter project

- Just update an empty timeline from a yWriter project.


For more information, see the [aeon2yw project page](https://peter88213.github.io/aeon2yw)


## Requirements

- [Python 3.6+](https://www.python.org).
- Aeon Timeline 2. Note: There is now a separate [converter for Aeon Timeline 3](https://peter88213.github.io/aeon3yw). 
- [novelyst v0.42+](https://peter88213.github.io/novelyst) 

## Download and install

[Download the latest release (version 0.2.0)](https://raw.githubusercontent.com/peter88213/aeon2yw_novelyst/main/dist/aeon2yw_v0.2.0.zip)

- Unzip the downloaded zipfile "aeon2yw_novelyst_v0.2.0.zip" into a new folder.
- Move into this new folder and launch **setup.pyw**. This installs the script for the local user.
- The plugin's features are accessible via the **Tools > Aeon Timeline 2** menu in *novelyst*.

------------------------------------------------------------------

[Changelog](changelog)


## License

aeon2yw_novelyst is distributed under the [MIT License](http://www.opensource.org/licenses/mit-license.php).


 




