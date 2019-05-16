# Tips and Tricks


## Comments at top of file show in hover
When you hover over the path of a linked file in the `run` field of a
workflow step, editors (such as VS Code) may offer a preview of the
file. If you take the first few lines of the CWL to write up a synopsis
of what the CWL does, this will then be shown on hover.

![](../media/hover-preview.png)


## Configuration
The configuration file is found under
`$XDG_CONFIG_HOME/sevenbridges/benten/config.ini` (If `$XDG_CONFIG_HOME`
is not set, `$HOME/.config/sevenbridges/benten/` is used)

On first startup benten will create a default configuration file for
you. The configuration file is in the .ini format and is fairly
self-explanatory. The default file can be found
[here](../benten/000.package.data/config.ini)


## Reporting bugs
Log files are found under `$XDG_DATA_HOME/sevenbridges/benten/logs` (If
`$XDG_DATA_HOME` is not set,
`$HOME/.local/share/sevenbridges/benten/logs` is used). The log from the
current run is `benten-ls.log`. Logs from previous runs are preserved in
a rotating fashion. These logs could be attached to bug reports as
needed. They do contain file names and paths.

