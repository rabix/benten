# VS Code plugin for Rabix/Benten CWL language server

<img height="400px" src="https://raw.githubusercontent.com/rabix/benten/master/media/2019.10.22/full-window.png"></img>

- Syntax highlighting (CWL and JS)
- Evaluate expression on hover
- File path autocomplete for linked files in `run` field
- Port completion for workflow
- Navigate to linked sub-workflows and includes (Jump to definition)
- Outline view (Symbols) + Step symbols
- Type validations
- Port validations

[(Click for feature screenshot gallery)](https://github.com/rabix/benten/blob/master/docs/features.md)


# Server installation

This plugin requires the [Benten CWL Language Server](https://github.com/rabix/benten) to be installed.

**If you install the server after loading a CWL file you will have to
restart VS Code.**

**If you are trying to reinstall or upgrade the server on windows with
VS Code running, you will have to exit VS Code, since it will be running
the server and will have locked it from changes.**

## Using pipx

A neat way to install `benten` in a virtual env (isolating it from your
system python) and still be able to call it as a regular executable is
to use `pipx`

```
pip3 install pipx  # in case you don't have pipx
pipx ensurepath # ensures CLI application directory is on your $PATH
pipx install benten
```

For more detailed information please see the [project page](https://github.com/rabix/benten).

<div align="right">
<sub>(c) 2019 Seven Bridges Genomics. Rabix is a registered trademark of Seven Bridges Genomics</sub>
</div>
