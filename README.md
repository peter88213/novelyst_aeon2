# aeon2yw_novelyst

An aeon2yw_novelyst plugin for novelyst.

For more information, see the [project homepage](https://peter88213.github.io/aeon2yw_novelyst) with description and download instructions.

## Development

*aeon2yw_novelyst* depends on the [pywriter](https://github.com/peter88213/PyWriter) and [aeon2yw](https://github.com/peter88213/aeon2yw) libraries which must be present in your file system. It is organized as an Eclipse PyDev project. The official release branch on GitHub is *main*.

### Mandatory directory structure for building the application script

```
.
├── PyWriter/
│   └── src/
│       └── pywriter/
├── aeon2yw/
│   └── src/
│      └── aeon2ywlib/
└── aeon2yw_novelyst/
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

aeon2yw_novelyst is distributed under the [MIT License](http://www.opensource.org/licenses/mit-license.php).
