The [novelyst](https://peter88213.github.io/novelyst/) Python program helps authors organize novels.  

The *novelyst_aeon2* plugin synchronizes novelyst projects with Aeon Timeline 2.

## Features

### Update an existing novelyst project from a timeline

- Update scene date, time, duration, description, tags, and relationships.
- Missing scenes, characters, locations, and items are created.
- Scenes are marked "unused" if the associated event is deleted in Aeon.

### Update an existing timeline from a novelyst project

- Update event date, time, duration, description, tags, and relationships.
- Entity types "Arc", "Character", "Location", and "Item", and a *Narrative* arc are created, if missing.
- Event properties "Description" and "Notes" are created, if missing.
- Missing events, characters, locations, and items are created.
- "Narrative" events are removed if the associated scene is deleted in novelyst.

### Create a new timeline from a novelyst project

- Just update an empty timeline from a novelyst project.


## Requirements

- Aeon Timeline 2. Note: There is now a separate [converter for Aeon Timeline 3](https://peter88213.github.io/aeon3yw). 
- [novelyst](https://peter88213.github.io/novelyst/) version 4.0+

## Download and install

[Download the latest release (version 0.99.0)](https://raw.githubusercontent.com/peter88213/novelyst_aeon2/main/dist/novelyst_aeon2_v0.99.0.zip)

- Unzip the downloaded zipfile "novelyst_aeon2_v0.99.0.zip" into a new folder.
- Move into this new folder and launch **setup.pyw**. This installs the plugin for the local user.

*Note: If you install novelyst at a later time, you can always install the plugin afterwards by running the novelyst_aeon2 setup script again.*

## Usage and conventions

See the [instructions for use](usage)

------------------------------------------------------------------

[Changelog](changelog)


## License

This is Open Source software, and the *novelyst_aeon2* plugin is licensed under GPLv3. See the
[GNU General Public License website](https://www.gnu.org/licenses/gpl-3.0.en.html) for more
details, or consult the [LICENSE](https://github.com/peter88213/novelyst_aeon2/blob/main/LICENSE) file.


 




