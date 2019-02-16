# Benten
## _(This software is in the very early stages of development)_

This is a workflow helper for [Common Workflow Language](https://www.commonwl.org/) documents.

<img align="right" width="100px" src="media/benten-icon.png">
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


# Configuration and log files

## Configuration
The configuration file is found under `$XDG_CONFIG_HOME/sevenbridges/benten/config.ini`
(If `$XDG_CONFIG_HOME` is not set, `$HOME/.config/sevenbridges/benten/` is used)

On first startup benten will create a default configuration file for you. The configuration
file is in the `.ini` format and is fairly self-explanatory:

```
[files]
autosave = True
autoload = False

[sbg]
credentials_file = /Users/kghose/.sevenbridges/credentials
```

## Logs
Log files are found under `$XDG_DATA_HOME/sevenbridges/benten/`
(If not set, `$HOME/.local/share/sevenbridges/benten/` is used)


# SBG app eco-system 

You can push your workflows/tools to your projects on any SBG based platform
(like [CGC], [CAVATICA], [Fair4Cures]) using the "Push" option on the menu.

[CGC]: https://cgc.sbgenomics.com
[CAVATICA]: https://cavatica.sbgenomics.com
[Fair4Cures]: http://f4c.sbgenomics.com/

## Credentials file and profiles

_Benten_ will look over your Seven Bridges API credentials file (`~/.sevenbridges/credentials`), 
if you have one, and list all your profiles on a "Contexts" menu. This menu allows you to select
a context that you can push (and pull) apps to. 

If you use the SBG API you already have an API configuration file. If not, you
should create one. It is usually located in `~/.sevenbridges/credentials` but _Benten_ allows
you to configure this by setting the path in the configurations file

Each section (e.g. `[cgc]`) is a profile name and has two entries. The end-point, (which is fixed
and you can copy from here), and an authentication token, which you get from your developer tab 
on the platform.

```
[default]
api_endpoint = https://api.sbgenomics.com/v2
auth_token   = 671998030559713968361666935769

[cgc]
api_endpoint = https://cgc-api.sbgenomics.com/v2
auth_token   = 282174488599599500573849980909

[cavatica]
api_endpoint = https://cavatica-api.sbgenomics.com/v2
auth_token   = 521419622856657689423872613771

[f4c]
api_endpoint = https://f4c-api.sbgenomics.com/v2
auth_token   = 362736035870515331128527330659
```

You can have several profiles on the same platform if, for example, you are an enterprise user and
you belong to several divisions. Please refer to the API documentation for more detail.


### Switching contexts while editing

Say you are editing a workflow in the context of your "CGC" profile, and you switch to your "Cavatica"
profile, where the current app and the nested apps are not present. When you go to push your app, 
_Benten_ will discover that the orginal project does not exist (probably). If so you will then get
a "Push dialog" that you got when originally pushing the app and you will have to fill out the
destination project and app id. Benten will then proceed to install this app in that project on
Cavatica. However, now you will no longer be able to change the versions of the subworkflows since
this history does not exist in the Cavatica repository. The workflow will work exactly the same
however. 

Typically, if you work in multiple contexts (which is very rare), it is most convenient to develop
on just one platform, and then distribute the final frozen workflows to collaborators on other
platforms.


## Pushing apps

The first time you push a particular App to an SBG end-point _Benten_ will ask for a project 
(and app id if you haven't added one). 

Each time you push _Benten_ may also offer you two options:
- Push dependents
- Inline this workflow

**Push dependents** means that there are apps included in the workflow that are in the SBG registry
and have been locally edited. Some care should be taken when doing this if you are sharing the
same tool locally with other users. Pushing dependents will push the current edited app and create
a new version. Existing workflows will not be affected, but a new App version will appear in
the repository which may not have been intended.

**Inline this workflow** is asking if you want _Benten_ to recursively go through each step and
put the code for the process referred to in the step into the workflow you are editing. This
changes your local code, and disconnects it from any local references you have made. 

(For reproducibility purposes, in the SBG repository, Apps are always stored inlined, as one document)


## Editing a pushed app 

When you edit a pushed app, _Benten_ will append the string `-local-edits` to the app id. This 
temporarily unlinks the app from the SBG eco system but reminds _Benten_ about it's origins. 
This app will no longer show the ability to change it's version though it will show the original 
version number on the workflow map with the word `edited`. This will remind you that you have
a step in your workflow that hasn't been pushed. Note that this goes only one level deep. 
Once you "push" the edited app again, _Benten_ will remove the `-local-edits` string from 
the app id and create a new version, and things are  back as they were (except that the App 
has a new version now) before.

This is useful when you want to test changes to an App in the context of a larger workflow, but 
don't want to commit changes to the App until you are done testing. 

## Breaking off from a previously pushed App

If you want to break off from the original App, i.e. you used that as a template, but now your
development has completely diverged and it's basically a new app, you can delete the `id` value
and replace it with a new one. Now, when you push the App _Benten_ will create a new app from
scratch.


## Switching version of Apps linked to the SBG eco-system

If an App has an SBG repository id, _Benten_ will allow you to change the version of the App.
On the workflow map such an App will have a version number on the tooltip, and right clicking
will bring up a version selection list that allows you to change the version of the workflow.
You can change the version of the current document by clicking on the "version" menu and selecting
the version you want.

This requires _Benten_ to pull the appropriate version of the app code from the platform store.
Currently (2019.02) the SBG backend stores the workflow in JSON format with some SBG specific
metadata. _Benten_ converts the JSON to YAML and strips out the non-essential metadata.
As you can guess this is not a complete round trip. So if you pushed a particularly formatted
YAML the first time to App version 10, added more changes to create version 11, and then you
switch back to version 10, currently (2019.02) you may not get your formatting back. 
Functionally, however, the CWL will be identical to the orginal version 10.

**Importantly** the code stored in the SBG repo is always completely self-contained, which means
all external references would have been resolved and frozen. It is this frozen app that you will
get back.


### Mass Update menu

Besides individually altering the versions of processes there are two "Mass Update" options.

One option, "Pull all latest", goes recursively through the workflow and updates all 
inline components to the latest versions available on the SBG repository. Linked processes
are not altered, since this would change other files locally.

The other option, "Push this to dependents" opens a simple dialog where you can choose a folder
to process. All workflows in that folder that have that process as a component will be altered
to use the current version of that process. This action is useful if you wish to force all
workflows to a specfic version of the given tool.

One of the options in that dialog is to "Push all changes", which if checked, will, in addition,
push these changed workflows to the SBG repository, creating a new version for each of them.


### Switching versions of an externally linked App

Since switching the version of an externally linked app will change its code, and will affect
any other workflows which refer to it _Benten_ does not allow you to do this. You should
inline that App and then change it's version as desired, which allows you to keep such changes
isolated from other workflows that depend on that app.


## In-lining, linking, Benten and the sbg app repository

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

# Suggested flow when using _Benten_, your own local repository and the SBG app repository

Since _Benten_ is directed at users who are extensively hand editing their CWL, presumably because
they care about the presentation of the code, and the ability to perform sensible diffs on it,
the following flow is suggested.

## Library of command line tools

As you create and test your command line tools, check them into your local repository as you 
normally do. When you are ready to share this tool, use push to publish this version to the 
SBG repository via _Benten_. At this point there will be a one line change to your code, with the
id assigned to that tool by the SBG repository and the SBG version number. This modified code
should also be checked in to keep a record. Each time you are ready to make an "official" version
you should push to the SBG repository and check the code in with the new app id.

## Workflows

When creating workflows try to include only tools and workflows that have already been checked
into the repository and opt to have them included inline even though this may slow you down.

During development it may be tempting to use links to external documents in order to use the latest
version of the tools your colleagues are putting out, but this can make debugging hard. It is more
convenient to inline everything, freezing your versions, and then consciously update particular
dependencies, or, if you are feeling particularly adventurous, do a mass update.

In some cases, your colleagues will pull rank on you and force push their update on you. But that
is a social matter for you all to sort out.

 
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

_References_
- [Wikipedia page](https://en.wikipedia.org/wiki/Benzaiten)
- [Benzaiten (Benten): Japan’s Goddess of Reason ](http://yabai.com/p/3200) - a much more detailed history

---

<div align="right">
<sub>(c) 2019 Seven Bridges Genomics. Rabix is a registered trademark of Seven Bridges Genomics</sub>
</div>