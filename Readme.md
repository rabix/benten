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

# Limitations/Quirks

## YAML flowstyle
YAML allows you to use a `flow style` which is very concise. If you put the top level
elements (`cwlVersion`, `class`, `steps` etc.) in flow style _Benten_ will not work for you. 
If you put the elements in the `step` field in flow style, _Benten_ will not work for you.

## Inline step editing and blank lines
If you have an inline step, and have a blank line with white-spaces, on editing the step these 
white-spaces will disappear from your blank line. In general it is a good practice not to have 
spurious whitespace in a blank line anyway ...


# Manual/Features

2019.02.12 preview
![2019.02.12 release](https://lh3.googleusercontent.com/1M5Qplw84aA6arEvgwLm9sxedjDgoCo3ZNL20lp7P3OfQYGqdStcDgrBgOiX6i2ke3apyyGulSBr3_gBVaohgPcq_4pvHsvxskjJCb_R9fxmxbo8Lg5UEEepVyc6-UKC3a2ov3sbVg=w2326-h1390-no)


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
workflow. A breadcrumb trail (AKA tabs) above the view keeps track of what 
steps the user has clicked through and the user can click on the trail to switch 
to an earlier view.

## Code editor
The code editor pane shows the raw code. This is the code that is being parsed to
show the workflow map and to perform auto-completion on the command bar.

Editing the raw CWL in the code editor tab will update the workflow map. Entering 
invalid YAML will lock out the workflow map and command bar until the YAML is 
fixed. Valid YAML that is invalid CWL will result in a workflow with warnings
and errors.

# A note on the modular nature of CWL

CWL has a very useful feature in that any CWL document (representing a unit of action) 
can be included in any CWL workflow as a step. In this manner CWL workflows can be
built up modularly from a library of tools, with workflows combining and nesting 
this library very simply to any depth needed.

CWL allows you to either link to an external CWL document by reference (much like 
an `include` or `import` statement in some languages) or to directly include the
code inline in the main document.

## To inline or not to inline

### Use cases for in-lining
- You want to freeze all components of the workflow for reproducibility purposes
- You want to share the complete CWL in a self contained form

### Use cases for linking
- You want to keep the parent workflow compact and easier to understand. You are
  confident that changes to the linked documents are systematic and under control. 
- You want your parent workflow to always reflect the current state of the linked 
  workflows


# SBG app eco-system 

You can push your workflows/tools to your projects on any SBG based platform
(like [CGC], [CAVATICA], [Fair4Cures]).

[CGC]: https://cgc.sbgenomics.com
[CAVATICA]: https://cavatica.sbgenomics.com
[Fair4Cures]: http://f4c.sbgenomics.com/

_Benten_ will look over your Seven Bridges API credentials file (`~/.sevenbridges/credentials`), 
if you have one, and list all your profiles on a "Contexts" menu. This menu allows you to select
a context that you can push (and pull) apps to.

The first time you push an App to an SBG end-point _Benten_ will ask for a project (and app id
if you haven't added one). It will also present you with the option to recursively 
inline the whole workflow on your side. Please refer to the notes on inlining to help
decide whether you want to do this.

(For reproducibility purposes, Apps are always stored inlined, as one document in the SBG repository)
See some hints below to decide if you want to recursively inline all components, or leave the
code as is with external references. 

Upon successfully pushing the App _Benten_ will modify your app id (or add one) to match the id 
on the SBG repository. _Benten_ can now use this to track versions of the app on the SBG repository.
The rest of your code is untouched, unless you have chosen to recursively inline dependents.

## Switching version of Apps linked to the SBG eco-system

If an App has an SBG repository id, _Benten_ will allow you to change the version of the App.
On the workflow map such an App will have a version number on the tooltip, and right clicking
will bring up a version selection list that allows you to change the version of the workflow.
You can change the version of the current document by clicking on the "version" menu and selecting
the version you want.

This requires _Benten_ to pull the appropriate version of the app code from the platform store.
Currently (2019.02) the SBG backend stores the workflow in JSON format with some SBG specific
metadata. _Benten_ converts the JSON to YAML and strips out the non-essential metadata. It
As you can guess this is not a complete round trip. So if you pushed a particularly formatted
YAML the first time to App version 10, added more changes to create version 11, and then you
switch back to version 10, currently (2019.02) you may not get your formatting back. 
Functionally, the CWL is identical.

### Switching versions of an externally linked App

Since switching the version of an externally linked app will change it's code, this will affect
any other workflows which refer to it.


## In-lining, linking, Benten and the sbg app ecosystem

The SBG app ecosystem and _Benten_ together try to combine some of the benefits of inlining and
linking. 

An inlined SBG app is it's own insulated unit and can be modified without affecting other
workflows and is isolated from changes to other workflows that it borrows steps from. However, 
through the proper use of the `id` field Benten can identify which Apps are copies of other 
Apps registered with the  SBG repo and inform the user which version they are on,
and inform them of what other versions of those Apps are available and selectively update the
relevant, inlined, nested workflow steps. 

The inlined app can form a large and complex CWL document. _Benten_ offers help by allowing users
to locate different logical parts of this big document and edit them in isolation.


# License
[Apache 2.0](LICENSE)


# Acknowledgments

The code editor is a trivially modified copy of the Pyzo code editor component 
distributed with the [Pyzo IDE](https://pyzo.org/about_pyzo.html). The Pyzo
code is distributed under the [BSD license](benten/gui/codeeditor/license.txt).
Many thanks to the Pyzo team for taking the care to modularize their code so
that it is so trivial to incorporate it in different projects. The design of the
editor is also very elegant, with additive functionality from mixins. 


# Developer notes
- [Ramblings of the developer](development-notes.md)
- [Roadmap (AKA todo notes)](roadmap.md)


# What's in a name? 

**Saraswati** is the Hindu goddess of learning and knowledge and a long time ago 
she visited Japan, where she is known as [Benzaiten] (**Benten** for short) and 
her sitar has morphed into a Japanese lute but she has kept some of her many arms.

Benzaiten is the goddess of everything that flows: water, time, words, speech, 
eloquence, music and by extension, knowledge. Therefore _Benten_ is an 
appropriate goddess for scientific workflow developers.

[Benzaiten]: https://en.wikipedia.org/wiki/Benzaiten 
