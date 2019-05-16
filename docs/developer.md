# How to setup and develop with VS Code

- Install benten
- Make sure the `benten-ls.sh` script is executable and in a location in the path
  e.g. /usr/local/bin
- Run `npm install` in this folder. This installs all the npm modules needed to
  compile the VS Code client extension.
- Run `tsc -b`
- Open VS Code on this folder.
- Press Ctrl+Shift+B to compile the client and server.
- Switch to the Debug viewlet.
- Select `Launch Client` from the drop down.
- Run the launch config.
- In the [Extension Development Host] instance of VSCode, open a CWL document
- In the [Extension Development Host] in the `output` tab, select "benten"


## Restart server

The development cycle is to modify the server code and then restart the server. 
Currently (04.2019) the only way to do this in VS Code is to use the 
"Reload Window" command:
CMD + Shift + P to bring up the command bar and then type "Reload Window".

## Code organization

```
|-- .vscode
|    |-- launch.json  - Creates a launch task for debugging
|     \- tasks.json
|-- src
|    \-- extension.ts - Client code for VS Code
|-- package.json      - declares entry points etc.
```

# VS Code web view

The VS Code documentation is extremely good.

- https://code.visualstudio.com/api/extension-guides/webview
- https://github.com/Microsoft/vscode/tree/master/extensions/markdown-language-features




# Distribution (WIP)

## Distributing the server
```
pip install cx_Freeze
```

## Distributing VS Code extension

https://code.visualstudio.com/api/working-with-extensions/publishing-extension
https://docs.microsoft.com/en-us/visualstudio/extensibility/adding-an-lsp-extension?view=vs-2019
https://code.visualstudio.com/api/references/extension-manifest

For local or test distribution we can use 
```
vsce package
```
and pass around the `.vsix` file for installing in VS Code



# Building distributions (WIP)

```
python setup.py sdist bdist_wheel
```

Upload to test pypi
```
python -m twine upload --repository-url https://test.pypi.org/legacy/ dist/*
```


Check distribution is working
```
python3 -m virtualenv ~/.venvs/test-benten
. ~/.venvs/test-benten/bin/activate
pip install --index-url https://test.pypi.org/simple/ --extra-index-url https://pypi.org/simple benten
```


# Things I learned

## Python

- Python's native ConfigParser will mangle your INI file keys. You have to override the
  `optionxform` function.
  https://stackoverflow.com/questions/1611799/preserve-case-in-configparser


## Pyside2 (Pyside is no longer used in this project)

- Get macOS to use a fixed width font:
  `setFont(QFontDatabase.systemFont(QFontDatabase.FixedFont))`

- Get `QTabWidget` to have tabs on the left side and looking “professional”
  `self.setDocumentMode(True)`

- An epic can be written about the confusing behavior of menus on macOS, but
  the main reading material is https://doc.qt.io/qt-5/qmenubar.html#qmenubar-as-a-global-menu-bar

- Don't do `menu.setNativeMenuBar(False)`: native mac is ... nicer

- When creating a QActionGroup you still need to add each individual action to the menu,
  not just the group.

- Stop signals from an object for a duration
  `blk = QSignalBlocker(self.code_editor)`