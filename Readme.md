# Benten
## _(This software is in the very early stages of development)_

This is a workflow helper for [Common Workflow Language](https://www.commonwl.org/) documents.

Many advanced CWL users are comfortable creating tools and workflows "by hand"
using a plain text editor. When creating complex enough workflows navigating 
and editing the resultant document and sub-documents can get tedious. Keeping
track of the bigger picture (what components have been added, what connections
have been set) can also get hard. _Benten_ is a CWL development tool that 
helps with navigating, visualizing and editing workflows. 

_Benten_ is written using Python and [Pyside2] (QT for Python)

[Pyside2]: https://doc.qt.io/qtforpython/

[![Tests](https://travis-ci.com/rabix/benten.svg?branch=master)](https://travis-ci.com/rabix/benten)
[![codecov](https://codecov.io/gh/rabix/benten/branch/master/graph/badge.svg)](https://codecov.io/gh/rabix/benten)


# Installation

Benten requires Python 3.7. (I prefer to set up a Python 3.7 virtual env)
```
python3 --version  # -> Python 3.7.1      (Verify python version)
python3 -m virtualenv ~/.venvs/benten   # Create virtual env - I prefer this
. ~/.venvs/benten                       # Activate virtual env
pip3 install git+https://github.com/rabix/benten.git            # Install from github master branch
# pip3 install git+https://github.com/rabix/benten.git@develop  # Install from github develop branch
benten -v <your-workflow-name.cwl>      # Open your-workflow-name.cwl in Benten with debug logging
```

# Limitations
YAML allows you to use a `flow style` which is very concise. If you put the top level
elements (`cwlVersion`, `class`, `steps` etc.) in flow style _Benten_ will not work for you. 
If you put the elements in the `step` field in flow style, _Benten_ will not work for you.


# Manual/Features

2019.02.10 preview
![2019.02.10 release](https://lh3.googleusercontent.com/Y9H2uBYkwrqd9tYwMUsa1be-7knH-yD4s2eR-sC0f0xPkY7DbBa6QFQukATKLqHDxHWP8l2_v0Ykpm3oouyfjO9b0Yxsfb315L0BgmStSIqN7SutyVq2Y3_jp2JFgpZcneNX79U0LGa5aORjHId-gx3EUwz5RAsNsE7pwLmCFJh2rYN-_L2Z8k_mkCAFn6LEK4PlnULcfpQDf8SDoYS4JzsTaW7LqCJWCa9w-6kX320_npxrpMmTqPK7vX4DZKC8KHLqb3D4Ls1j9JCdliZSykLzwrF4adzgVz8PI1CQLFuReN0dRuaFdrgCv_bVrUHM4U2g2G1q9ODUdFXBYCK0ACx9bdSGX_xFW5RUoCgyouR7HBZ228Yu_y5-eDkF-Fiz4zHqnLZBOaEA2ZYV5-706bekpWzZKk31hcnlcVQldK6IzlpE_MXKaGkoQRQJegf0-YTodmo7o5OATcmtXpcVxsXTo-gzG40DVS0hJoM9gTXSIPI4aX5yUf-wf9gaxwqf3D_UFI8xgZhfBFRiCIb8-NaXRQpSJx_1xTzFeohK06PPVPiJ8CWSW1yeaa0W1A8nmjvQ0JYdUevS432wYAKxlctFlmkpsxx7SJdcin37VjBN7czbZ72S0StqOAXAOPcjPnUl2T3N3uU-enW5YAYY1rSe2TL0LV3MnPGcVgFYBNjGfF3g3kdrQ0BTmw_E-wpUZQyBITu0aBHoVhWVfl4U3qcq=w2062-h1096-no)

Benten has three main panes: Workflow map, Code editor and Connection table. The
relative sizes of each can be changed by dragging dividing lines up/down, left/right.


## Workflow map
The workflow map gives an overview sketch of the workflow. Individual port 
connections are not shown: the workflow DAG just indicates the overall flow of 
data from input to out via the various process steps. 
A hierarchical layout is used that emphasizes the dataflow.

Clicking on a flow line connecting two nodes will populate the connection table 
with all the connections between those two nodes.

Clicking on a node will focus on it. This scrolls the code editor to
the code for that step and populates the connection table.

Clicking on the input or output node will show all the input/output connections
of the workflow on the connection table.

Double-Clicking on a step will switch the view to show this step. Editing
inlined steps has some behaviors to note. Please see "Editing inlined steps" below.

A breadcrumb trail (tabs) above the view keeps the user oriented. Clicking on 
a tab switches to the view to that step.


### Editing inlined steps

If a step is a subworkflow referring to another file, this is just like having 
different files open in different editor instances. If the step is inline, however, 
then edits in the different views are actually edits to the same file. 
In such a case edit history operates a little specially. In the view where an
edit is done, a normal history of edits evolves. In the other views a squashed
edit is applied when switching to that view, so the history is less rich.

Say your main workflow is "A", being edited in view 1. It has an inlined step "A.s1". 
This inlined step also has an inlined step "A.s1.s2". You click on "A.s1" to open that 
in a new view (2). In the new view (2) showing "A.s1" you click on "A.s1.s2" and 
open *that* in yet another view (3).

Via the breadcrumbs you are free to switch to any of the views and edit from there. 
If, say, you are in view 1 (showing all of "A") and you delete "A.s1" then the 
two child views 2 and 3 will be closed. If you go to view 2 (showing "A.s1") and edit 
the node "A.s1.s2" then switch back to view 1, it will reflect the changes.
If you switch to view 3, it will reflect those same edits too.


## Breadcrumb trail

As mentioned earlier, views can switch to displaying a step within the current 
workflow. A breadcrumb trail above the view keeps track of what steps the user
has clicked through and the user can click on the trail to switch to an earlier
view.

## Code editor
The code editor pane shows the raw code. This is the code that is being parsed to
show the workflow map and to perform auto-completion on the command bar.

Editing the raw CWL in the code editor tab will update the workflow map. Entering 
invalid YAML will lock out the workflow map and command bar until the YAML is 
fixed. Valid YAML that is invalid CWL will result in a workflow with warnings
and errors.


# License
Apache 2.0


# What's in a name? 

**Saraswati** is the Hindu goddess of learning and knowledge and a long time ago 
she visited Japan, where she is known as [Benzaiten] (**Benten** for short) and 
her sitar has morphed into a Japanese lute but she has kept some of her many arms.

Benzaiten is the goddess of everything that flows: water, time, words, speech, 
eloquence, music and by extension, knowledge. Therefore _Benten_ is an 
appropriate goddess for scientific workflow developers.

[Benzaiten]: https://en.wikipedia.org/wiki/Benzaiten 
