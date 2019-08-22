# Benten (pre-alpha) 

This is a [language server] for [Common Workflow Language](https://www.commonwl.org/) documents.

<img align="right" height="150px" src="media/benten-icon.png"></img>
Many advanced CWL users are comfortable creating tools and workflows "by hand"
using a plain text editor. When creating complex enough workflows navigating 
and editing the resultant document and sub-documents can get tedious. Keeping
track of the bigger picture (what components have been added, what connections
have been set) can also get hard. 

_Benten_ is a language server that offers help with code snippets, 
navigation and syntax checking of CWL documents.

_Benten_ is written using Python3 and developed against VS Code. The language
server component will work with any editor/IDE that offers language server
support. Syntax highlighting is currently only available for the VS Code
extension. The VS Code extension is written in Typescript.

[language server]: https://langserver.org/

[![Tests](https://travis-ci.com/rabix/benten.svg?branch=master)](https://travis-ci.com/rabix/benten)
[![codecov](https://codecov.io/gh/rabix/benten/branch/master/graph/badge.svg)](https://codecov.io/gh/rabix/benten)
[![Codacy Badge](https://api.codacy.com/project/badge/Grade/20839ce29ebe4004b3578d4d02031a1c)](https://www.codacy.com/app/kaushik-work/benten?utm_source=github.com&amp;utm_medium=referral&amp;utm_content=rabix/benten&amp;utm_campaign=Badge_Grade)

# Features Implemented (version 2019.05.31)

![2019.04.23](https://i.imgur.com/fgJOXum.png)

- CWL syntax highlighting, CWL grammar parsing _(1)_
- Embedded JS expression highlighting _(2)_
- Navigate to linked sub-workflows _(3)_
- Outline view (Symbols) + Step symbols _(4)_
- Code snippets for process types, inputs, requirements
- Error squiggles indicating YAML and CWL issues
- File path autocomplete for linked files in `run` field


# Server installation

Benten requires [Python 3.7 or later](https://www.python.org/downloads/)

If you will be installing from source you will need
[git](https://git-scm.com/downloads) on your system

A neat way to install `benten` in a virtual env (isolating it from your
system python) and still be able to call it as a regular executable is
to use `pipx`

```
pip3 install pipx  # in case you don't have pipx
pipx install --spec git+https://github.com/rabix/benten.git benten
```

_Note: `pipx` installs the executables in `$HOME/.local/bin`
(`%HOMEPATH%\.local\bin` for Windows). This needs to be added to your
PATH env variable_

To install from develop branch (or some other branch): 
```
pipx install --spec git+https://github.com/rabix/benten.git@develop benten
```

Or, if you have cloned the repository and want to play with the server
code itself:

```
pipx install -e benten
```


# Install VS Code extension

- Download the VS Code extension file (.vsix) from the releases page
- In the extensions pane on VS Code use "Install from VSIX..." to install this .vsix file

# Using with VI/Vim

See [this page](docs/vim.md) please.


# Tips and Tricks

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
<sub>(c) 2019 Seven Bridges Genomics. Rabix is a registered trademark of Seven Bridges Genomics</sub>
</div>
