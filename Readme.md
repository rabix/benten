# Benten 

This is a [language server] for [Common Workflow Language](https://www.commonwl.org/) documents.

<img align="right" height="150px" src="media/benten-icon.png"></img>
Many advanced CWL users are comfortable creating tools and workflows "by
hand" using a plain text editor. When creating complex enough workflows,
navigating and editing the resultant document and sub-documents can get
tedious. Keeping track of the bigger picture (what components have been
added, what connections have been set) can also get hard.

_Benten_ is a language server that offers help with code completion,
navigation and syntax checking of CWL documents.

_Benten_ is written using Python3 and developed against VS Code. The language
server component will work with any editor/IDE that offers language server
support. Syntax highlighting is currently only available for the VS Code
extension. The VS Code extension is written in Typescript.

[language server]: https://langserver.org/

[![Tests](https://travis-ci.com/rabix/benten.svg?branch=master)](https://travis-ci.com/rabix/benten)
[![codecov](https://codecov.io/gh/rabix/benten/branch/master/graph/badge.svg)](https://codecov.io/gh/rabix/benten)
[![Codacy Badge](https://api.codacy.com/project/badge/Grade/20839ce29ebe4004b3578d4d02031a1c)](https://www.codacy.com/app/kaushik-work/benten?utm_source=github.com&amp;utm_medium=referral&amp;utm_content=rabix/benten&amp;utm_campaign=Badge_Grade)

# Features

![2019.09.03](https://i.imgur.com/fgJOXum.png)

- CWL syntax highlighting, CWL grammar parsing
- JS Expression highlighting
- Evaluate expression on hover
- File path autocomplete for linked files in `run` field
- Port completion for workflow
- Navigate to linked sub-workflows and includes
- Outline view (Symbols) + Step symbols
- Error squiggles indicating YAML and CWL issues


# Server installation

Benten requires [Python 3.7 or later](https://www.python.org/downloads/)

If you will be installing from source you will need
[git](https://git-scm.com/downloads) on your system

## Special instructions for Ubuntu Linux

```
sudo apt install python3-pip python3-venv
```

## Using pipx

A neat way to install `benten` in a virtual env (isolating it from your
system python) and still be able to call it as a regular executable is
to use `pipx`

```
pip3 install pipx  # in case you don't have pipx
pipx ensurepath # ensures CLI application directory is on your $PATH
pipx install --spec git+https://github.com/rabix/benten.git benten
```

_Note: `pipx` installs the executables in `$HOME/.local/bin`
(`%HOMEPATH%\.local\bin` for Windows). This needs to be added to your
PATH env variable. `pipx ensurepath` does this for you_

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

Search for "Benten" in the marketplace. The name of the client extension
is Rabix/benten. Follow the usual method to install the extension.

# Using with VI/Vim

See [this page](docs/vim.md) please.


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
