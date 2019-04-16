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
support. Code snippets are currently only available for VS Code.

[language server]: https://langserver.org/

[![Tests](https://travis-ci.com/rabix/benten.svg?branch=master)](https://travis-ci.com/rabix/benten)
[![codecov](https://codecov.io/gh/rabix/benten/branch/master/graph/badge.svg)](https://codecov.io/gh/rabix/benten)


# Installation

Benten requires Python 3.7. (I prefer to set up a Python 3.7 virtual env)
```
python3 --version  # -> Python 3.7.1      (Verify python version)
python3 -m virtualenv ~/.venvs/benten   # Create virtual env - I prefer this
. ~/.venvs/benten/bin/activate          # Activate virtual env
pip3 install git+https://github.com/rabix/benten.git            # Install from github master branch
# pip3 install git+https://github.com/rabix/benten.git@develop  # Install from github develop branch
```

# Features Implemented (release 2019.04.16)
- Code snippets for process types, inputs, requirements
- Error squiggles indicating YAML and CWL issues
- Navigate to linked sub-workflows via "Goto Definition": Right-click on `run` field, or hit F12

# Run with VS Code

Please see the instructions [here](vscode-client/Readme.md)


# License
[Apache 2.0](LICENSE)


# Acknowledgments

The low level client-server communication [code][jsonrpc-code] is taken from [Sourcegraph's
(now defunct) Python Language Server][sourcegraph-python] as is the VS Code client code (which
was based originally off Microsoft's example code)

[jsonrpc-code]: https://github.com/sourcegraph/python-langserver/blob/master/langserver/jsonrpc.py
[sourcegraph-python]: https://github.com/sourcegraph/python-langserver


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