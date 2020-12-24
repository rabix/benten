# Benten

This is a [language server] for
[Common Workflow Language](https://www.commonwl.org/) documents.

[language server]: https://langserver.org/

### Server
[![Tests](https://travis-ci.com/rabix/benten.svg?branch=master)](https://travis-ci.com/rabix/benten)
[![codecov](https://codecov.io/gh/rabix/benten/branch/master/graph/badge.svg)](https://codecov.io/gh/rabix/benten)
[![Codacy
  Badge](https://api.codacy.com/project/badge/Grade/20839ce29ebe4004b3578d4d02031a1c)](https://www.codacy.com/app/kaushik-work/benten?utm_source=github.com&amp;utm_medium=referral&amp;utm_content=rabix/benten&amp;utm_campaign=Badge_Grade)
[![PyPI
  version](https://badge.fury.io/py/benten.svg)](https://badge.fury.io/py/benten)
  [![Conda
  Version](https://img.shields.io/conda/vn/conda-forge/benten.svg)](https://anaconda.org/conda-forge/benten)

### VS Code client 

[![Visual Studio Marketplace
  Version](https://img.shields.io/visual-studio-marketplace/v/sbg-rabix.benten-cwl?label=VS%20Code%20Ext)](https://marketplace.visualstudio.com/items?itemName=sbg-rabix.benten-cwl)
[![Open
  VSX](https://img.shields.io/open-vsx/v/sbg-rabix/benten-cwl)](https://open-vsx.org/extension/sbg-rabix/benten-cwl)


## Features

[(Click for feature screenshot gallery)](https://github.com/rabix/benten/blob/master/docs/features.md)

- Syntax highlighting (CWL and JS)
- Evaluate expression on hover
- File path autocomplete for linked files in `run` field
- Port completion for workflow
- Navigate to linked sub-workflows and includes (Jump to definition)
- Outline view (Symbols) + Step symbols
- Type validations
- Port validations
- Display language documentation on hover

![Benten + VS Code](https://raw.githubusercontent.com/rabix/benten/master/media/2019.12.03/full-window.png)


_Benten_ is written using Python3 and developed against VS Code. The language
server component will work with any editor/IDE that offers language server
support. Syntax highlighting is currently only available for the VS Code
extension. The VS Code extension is written in Typescript.

# Install VS Code extension

Search for
"[Benten](https://marketplace.visualstudio.com/items?itemName=sbg-rabix.benten-cwl)"
in the marketplace. The name of the client extension is Rabix/benten. Follow the
usual method to install the extension.

If you have not installed the Benten server separately (see below) then the
client will attempt to find and download a matching server version from the
github releases page.

# Server installation

Benten requires [Python 3.7 or later](https://www.python.org/downloads/)

If you will be installing from source you will need
[git](https://git-scm.com/downloads) on your system


## Using pipx

A neat way to install `benten` in a virtual env (isolating it from your
system python) and still be able to call it as a regular executable is
to use `pipx`

```
pip3 install pipx  # in case you don't have pipx
pipx ensurepath # ensures CLI application directory is on your $PATH
```

Now you can install Benten with
```
pipx install benten
```

If you already have Benten installed you can upgrade it
```
pipx upgrade benten
```


If your base python install is earlier than 3.7 you can tell `pipx` to use 3.7 for Benten
```
pipx install benten --python python3.7
```


Notes:

1. `pipx` installs the executables in `$HOME/.local/bin`
   (`%HOMEPATH%\.local\bin` for Windows). This needs to be added to your
   PATH env variable. `pipx ensurepath` does this for you
2. `pipx install` can be done from within another virtual environment.
   This is helpful when you have an incompatible global version of
   Python which you wish to keep but still want to install Benten. You
   can create a virtual env with Python > 3.7 and invoke the
   installation commands from there.
3. If you are using VS Code, if you install the server after loading a CWL file
   you will have to restart VS Code.

### Special instructions for Ubuntu Linux

```
sudo apt install python3-pip python3-venv
```

### Note for Windows
If you are trying to reinstall or updating the server on windows with
the server running (e.g. because you have VS Code running), you will
have to shutdown the server (e.g. by exiting VS Code) before updating.


### Installing versions directly from github

To install from the master branch
```
pipx install git+https://github.com/rabix/benten.git
```

To install from develop branch (or some other branch):
```
pipx install git+https://github.com/rabix/benten.git@develop
```

Or, if you have cloned the repository and want to play with the server
code itself:
```
pipx install -e benten  # benten is the name of the directory with the cloned code
```

# Using with VI/Vim

See [this page](https://github.com/rabix/benten/blob/master/docs/vim.md) please.


# Expression evaluations on hover

Hovering over an expression will display the result of the evaluation or
any errors that are encountered. Benten auto-generates sample process
inputs, outputs and intermediate outputs (if the process is a workflow).
Note that these are all randomly generated sample data meant for quick
sanity checking of expressions.


## Over-riding auto-generated sample data

The sample data is auto-generated on demand when an evaluation is
requested. The generated sample data is also stored in a scratch file.
This scratch file can be accessed by clicking "go to definition" when
over any expression. Normally this file is just overwritten each time
with fresh, randomly generated data.

If you wish to customize some of the sample data (for example you have
specific test cases you want to check as you code the workflow) if you
add the string (exactly)

```
#custom
```

to the first line of the sample data file, Benten will stop overwriting
the file and use the contents of this customized file instead.

**Once you add this line to the sample data file, Benten will no longer
overwrite this file. If you want the test data to be regenerated (e.g.
you've changed the input schema of the CWL) you need to remove this
first sentinel line and Benten will regenerate the input.**


# Other tips and Tricks

Benten attaches onto your regular text editor and offers help by
way of auto-completions and document validations, so most of its
functionality is exposed naturally via the editor's regular UI, and a
specialized tutorial is not necessary, but some helpful
[tips and tricks](docs/tips.md) are listed in this page.


# For developers
See the [development documentation](docs/developer.md)


# License
[Apache 2.0](LICENSE)


# Acknowledgments

[Peter Amstutz](https://github.com/tetron/) for the PyInstaller formula and the
auto-downloading feature on the VS Code extension.

[Peter van Heusden](https://github.com/pvanheus/) for the
Benten Conda [distribution](https://github.com/conda-forge/benten-feedstock).

The low level client-server communication [code][jsonrpc-code] is taken from [Sourcegraph's
(now defunct) Python Language Server][sourcegraph-python] as is the VS Code client code (which
was based originally off Microsoft's example code). The CWL preview uses [vis.js]

[jsonrpc-code]: https://github.com/sourcegraph/python-langserver/blob/master/langserver/jsonrpc.py
[sourcegraph-python]: https://github.com/sourcegraph/python-langserver
[vis.js]: http://visjs.org/

# What's in a name?

**Saraswati** is the Hindu goddess of learning and knowledge and a long time ago
she visited Japan, where she is known as [Benzaiten] (**Benten** for short) and
her sitar has morphed into a Japanese _biwa_ but she has kept some of her many arms.

Benzaiten is the goddess of everything that flows: water, time, words, speech,
eloquence, music and by extension, knowledge. Therefore _Benten_ is an
appropriate goddess for scientific workflow developers.

[Benzaiten]: https://en.wikipedia.org/wiki/Benzaiten

_References_
- [Wikipedia page](https://en.wikipedia.org/wiki/Benzaiten)
- [Benzaiten (Benten): Japan’s Goddess of Reason ](http://yabai.com/p/3200) - a much more detailed history

---

<div align="right">
<sub>(c) 2019-2021 Seven Bridges Genomics. Rabix is a registered trademark of Seven Bridges Genomics</sub>
</div>
