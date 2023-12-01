# Notes for developers

## Debugging the server
Open the project in PyCharm. Goto `Run->Attach To Process` and then
select the process titled `benten-ls`. Insert appropriate breakpoints
and perform some editor operation that will trigger a request from the
client.

## Install a library directly into a `pipx` env

```
pipx inject -e benten cwlformat
```

### Release server on PyPi

```
python3 setup.py sdist bdist_wheel
twine upload dist/*
```

## How to setup and develop with VS Code

- Optional: Install benten (as outlined on the main Readme)
- From the `vscode-client` directory
  ```
  npm install -g typescript
  npm install
  ```
- Open the `vscode-client` directory in VS Code.
- Press Ctrl+Shift+B to compile the client and server.
- Switch to the Debug viewlet.
- Select and run `Launch Client` from the drop down.
- In the [Extension Development Host] instance of VSCode, open a CWL document
- In the [Extension Development Host] in the `output` tab, select "benten"

### Restart server

The development cycle is to modify the server code and then restart the server.
Currently (04.2019) the only way to do this in VS Code is to use the
"Reload Window" command:
CMD + Shift + P to bring up the command bar and then type "Reload Window".


### Release on VS Code Marketplace

Ensure version strings are synchronized
1. Version string in Python package
2. Version string in `package.json` for the VS Code extension
3. Version tag in the github release

This is because the VS Code extension takes it's version from the `package.json`
and looks for the corresponding release on github which in turn has the
`benten-ls` executable in a folder that is named with the Python version.

```
npm install -g typescript
npm install
npm install -g vsce
vsce package
```

Upload the `.vsix` file to [Marketplace]

[Marketplace]:
https://marketplace.visualstudio.com/items?itemName=denbi.denbi-benten-cwl


### Code organization

```
|-- .vscode
|    |-- launch.json  - Creates a launch task for debugging
|     \- tasks.json
|-- src
|    \-- extension.ts - Client code for VS Code
|-- package.json      - declares entry points etc.
```

## JS evaluation

If `dukpy` ever fails us we could consider simply doing

```
import subprocess
subprocess.check_output(['node', '-p', "function foo() {return 'hi';}; foo()"])
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

## VS Code: Message passing between extension and web view + scroll to line

- https://code.visualstudio.com/api/extension-guides/webview#scripts-and-message-passing
	canonical message passing reference

- https://github.com/Microsoft/vscode/issues/6695
	Shows simple code snippet for scrolling document

- https://github.com/Microsoft/vscode/issues/63073
	Has a code snippet showing how to scroll document to a line as
	well as message passing

- https://github.com/microsoft/vscode/issues/8886
	Discussion about window.visibleTextEditors

## Creating packages for everything

Use `make dist-pkg`

## Packaging with fpm

We can use fpm to create a `benten-ls` deb/rpm package which does
not depend on system Python or installing additional packages.

```
$ python=python-3.7
$ version=1.0
$ gem install --user fpm
$ virtualenv --python python3 build-fpm/usr/share/$python/dist/benten
$ build-fpm/usr/share/python-3.7/dist/benten/bin/pip install .
$ fpm -s dir -t deb -v $version -n benten -C build-fpm --depends python3 usr/share/$python/dist/benten/bin/benten-ls=/usr/bin/ .

```
