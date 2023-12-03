# novelyst_aeon2

An *Aeon Timeline 2* converter plugin for novelyst.

For more information, see the [project homepage](https://peter88213.github.io/novelyst_aeon2) with description and download instructions.

## Feedback? Ideas? Feature requests?

You can go to the [novelyst "discussions" forum](https://github.com/peter88213/noveltree/discussions) and start a thread.

# Contributing

## How to provide translations

First, you need to know your language code according to ISO 639-1.

For English, this is, for example, `en`, for German, it is `de`.

**NOTE:** The procedure described below is greatly simplified if you create a language pack based on the [novelyst_xx](https://github.com/peter88213/noveltree_xx) template and use the tools provided for this purpose. 

### Create a message catalog

A "message catalog" is a dictionary for the plugin's messages and menu entries.

For creating a message catalog, you download a template with all English messages from [here](https://github.com/peter88213/noveltree_aeon2/blob/main/i18n/messages.pot). 


Rename `messages.pot` to `<your language code>.po`, then give some specific information in the header data by modifying the following lines:

```
"PO-Revision-Date: YEAR-MO-DA HO:MI+ZONE\n"
"Last-Translator: FULL NAME <EMAIL@ADDRESS>\n"
"Language: LANGUAGE\n"
```

**NOTE:** Be sure to use a text editor that writes utf-8 encoded text. Otherwise, it may not work with non-ASCII characters used in your language.

The  `<your language code>.po` dictionary is organized as a set of *message ID (msgid)* - *message string (msgstr)* pairs, where *msgid* means the English term, and *msgstr* means the translated term. This is an example for such a pair where the message string is still missing:

```
msgid "Cannot overwrite file"
msgstr ""
```

Now you enter all missing message strings. 
- If a message ID contains placeholders like `{}`, be sure to put them also into the message string.  
- If a message ID starts with `!`, the message string must also start with `!`. 

Before you distribute your translations, you can convert and install the message catalog for testing. 

### Convert the message catalog to binary format

The plugin needs the message catalog in binary format. This is easily achieved using the **msgfmt.py** converter script. 
You find it in your Python installation, in the **Tools/i18n** subdirectory. If not, you can download the code from [here](https://github.com/python/cpython/blob/main/Tools/i18n/msgfmt.py)

Name the binary file **novelyst_aeon2.mo**. 


### Install your translation for testing

Add a subdirectory tree to **novelyst/locale**, and place *novelyst_aeon2.mo* there, like this:

```
<your home directory>
└── .novxlib/
    └── novelyst/
        └── locale/
            └─ <language code>/
               └─ LC_MESSAGES/
                  └─ novelyst_aeon2.mo
```

Then start *novelyst* and see whether your translation works. 

**NOTE:** At startup, *novelyst* tries to load a message dictionary that fits to the system language. If it doesn't find a matching language code in the *locale* directory, it uses English as default language. 

**HINT:** *novelyst_aeon2* comes with German translations. Look at the `de` directory tree, if you need an example. 


### Contribute your translations

If *novelyst* works fine with your translations, you can consider contributing it. 

An easy way may be to put a posting in the [novelyst forum](https://github.com/peter88213/noveltree/discussions), appending your  `<your language code>.po` file. 


## Development

*novelyst_aeon2* depends on the [novxlib](https://github.com/peter88213/novxlib) and [aeon2nv](https://github.com/peter88213/aeon2nv) libraries which must be present in your file system. It is organized as an Eclipse PyDev project. The official release branch on GitHub is *main*.

### Mandatory directory structure for building the application script

```
.
├── novxlib/
│   └── src/
│       └── novxlib/
├── aeon2nv/
│   └── src/
│      └── aeon2nvlib/
└── novelyst_aeon2/
    ├── src/
    ├── test/
    └── tools/ 
        └── build.xml
```

### Conventions

See https://github.com/peter88213/novxlib/blob/main/docs/conventions.md

## Development tools

- [Python](https://python.org) version 3.10.
- [Eclipse IDE](https://eclipse.org) with [PyDev](https://pydev.org) and *EGit*.
- *Apache Ant* is used for building the application.

## License

This is Open Source software, and the *novelyst_aeon2* plugin is licensed under GPLv3. See the
[GNU General Public License website](https://www.gnu.org/licenses/gpl-3.0.en.html) for more
details, or consult the [LICENSE](https://github.com/peter88213/noveltree_aeon2/blob/main/LICENSE) file.
