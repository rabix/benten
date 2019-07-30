# Notes for developers

## Debugging the server
Open the project in PyCharm. Goto `Run->Attach To Process` and then
select the process titled `benten-ls`. Insert appropriate breakpoints
and perform some editor operation that will trigger a request from the
client.


## How to setup and develop with VS Code

- Install benten (as outlined on the main Readme)
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


### Restart server

The development cycle is to modify the server code and then restart the server. 
Currently (04.2019) the only way to do this in VS Code is to use the 
"Reload Window" command:
CMD + Shift + P to bring up the command bar and then type "Reload Window".

### Code organization

```
|-- .vscode
|    |-- launch.json  - Creates a launch task for debugging
|     \- tasks.json
|-- src
|    \-- extension.ts - Client code for VS Code
|-- package.json      - declares entry points etc.
```

## VS Code: embedding one language in another

https://code.visualstudio.com/api/language-extensions/syntax-highlight-guide#embedded-languages


## VS Code: web view

The VS Code documentation is extremely good.

- https://code.visualstudio.com/api/extension-guides/webview
- https://github.com/Microsoft/vscode/tree/master/extensions/markdown-language-features


## VS Code: distributing extension

https://code.visualstudio.com/api/working-with-extensions/publishing-extension
https://docs.microsoft.com/en-us/visualstudio/extensibility/adding-an-lsp-extension?view=vs-2019
https://code.visualstudio.com/api/references/extension-manifest

For local or test distribution we can use 
```
vsce package
```
and pass around the `.vsix` file for installing in VS Code


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