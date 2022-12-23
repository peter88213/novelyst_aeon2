# novelyst_aeon2

An *Aeon Timeline 2* converter plugin for novelyst.

For more information, see the [project homepage](https://peter88213.github.io/novelyst_aeon2) with description and download instructions.

## Development

*novelyst_aeon2* depends on the [pywriter](https://github.com/peter88213/PyWriter) and [aeon2yw](https://github.com/peter88213/aeon2yw) libraries which must be present in your file system. It is organized as an Eclipse PyDev project. The official release branch on GitHub is *main*.

### Mandatory directory structure for building the application script

```
.
├── PyWriter/
│   └── src/
│       └── pywriter/
├── aeon2yw/
│   └── src/
│      └── aeon2ywlib/
└── novelyst_aeon2/
    ├── src/
    ├── test/
    └── tools/ 
        └── build.xml
```

### Conventions

- Minimum Python version is 3.6. 
- The Python **source code formatting** follows widely the [PEP 8](https://www.python.org/dev/peps/pep-0008/) style guide, except the maximum line length, which is 120 characters here.

### Development tools

- [Python](https://python.org) version 3.9
- [Eclipse IDE](https://eclipse.org) with [PyDev](https://pydev.org) and [EGit](https://www.eclipse.org/egit/)
- [Apache Ant](https://ant.apache.org/) for building the application script


## License

This is Open Source software, and the *novelyst_aeon2* plugin is licensed under GPLv3. See the
[GNU General Public License website](https://www.gnu.org/licenses/gpl-3.0.en.html) for more
details, or consult the [LICENSE](https://github.com/peter88213/novelyst_aeon2/blob/main/LICENSE) file.
