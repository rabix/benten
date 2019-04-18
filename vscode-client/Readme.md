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


# Code organization

```
|-- .vscode
|    |-- cwl.code-snippets  - Code snippets under development
|    |-- launch.json  - Creates a launch task for debugging
|-- src
|    |-- extension.ts
```
