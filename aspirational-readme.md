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

[![Tests](https://travis-ci.com/rabix/benten.svg?branch=develop)](https://travis-ci.com/rabix/benten)
[![codecov](https://codecov.io/gh/rabix/benten/branch/develop/graph/badge.svg)](https://codecov.io/gh/rabix/benten)


`Benten` the GUI workflow helper has four main panels that work in concert
to provide a "View" into a workflow.

## Workflow map
The workflow map gives an overview sketch of the workflow. Individual port 
connections are not shown: the workflow DAG just indicates the overall flow of 
data from input to out via the various process steps. 
A hierarchical layout is used that emphasizes the dataflow.

Dropping CWL files onto this map will add them as steps to the workflow.

Clicking on a flow line connecting two nodes will populate the inbound 
and outbound connection table with all the connections between those
two nodes.

Clicking on a step will focus on that node. This scrolls the code editor to
the code for that step and populates the inbound and outbound connection table
with the inputs and outputs for that node. Hitting delete while focused on a 
node will delete that node.

Clicking on the input or output node will show all the input/output connections
of the workflow on the connection table.

Double-Clicking on a step will switch the View to show this step. Editing
inlined steps has some behaviors to note. Please see "Editing inlined steps" below.

A breadcrumb trail above the views keeps the user oriented. Clicking on a breadcrumb
switches to the view to that step.

Selecting multiple steps enables the option to `implode` these steps into a
subworkflow. You will be asked for a file path to save the new step into. 
Leaving it blank creates an inline step. 

Choosing `extract`, instead, on one or more steps will pack this code into a 
separate process object (`Workflow`, `CommandLineTool` etc.) in a file you choose.

Selecting a step and asking for `inline` will copy all the code into the main
workflow file if the step refers to an external file.

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

The code editor has infinite undo/redo (within sanity). Any sub-workflow files 
created on disk are not undone, so undoing an implode step will leave the created 
subworkflow file intact.


## Error notifications

If a workflow has errors, an extra gutter will appear next to the line numbers and
red dots will appear. Hovering on the red dots with the mouse will present a message
indicating the error. Errors that pertain to the whole workflow, or which can not
be localized are all piled into line 1. 


## Command bar

Major workflow operations are performed using the command bar. The command bar
has auto complete which allows users to quickly navigate to the step and port
they want to access/modify

### Commands
```
as step_id path/to/step.cwl  - add step with given id
remove-step step_id          - remove step
ai input_id                  - add workflow input
remove-input input_id        - remove workflow input
ao output_id                 - add workflow output
remove-output output_id      - remove workflow output
c src dst                    - connect source to destination
disconnect src dst                    - disconnect
implode new_step_id (path/to/new.cwl | inline) step1_id step2_id step3_id 
                             - refactor the given steps into a single sub-workflow
                               Instead of path use the text "inline" to implode the step inline 
                               in the main document
explode step_id (path/to/folder) - given a step break it into individual tools in given folder 
export step_id path/to/new.cwl  - export CWL in given step if it is inline  
inline step_id path/to/step.cwl  - if step is a subworkflow make it inline in the main workflow

run                          - run current app. If the document name is x.cwl assumes that
                               there is a job file called x.job.yaml in same directory
                               uses system defined cwl-runner
```

#### SBG app ecosystem specific commands
```
sbg-profile       - set profile from credentials file 
                    (can also be set in config file or command line)

sbg-push          - push app (create revision) to SBG platform

not-sbg-apps      - mark whole session as not having SBG apps
sbg-apps          - mark session as having SBG apps (default)
```

Note that undo and redo operations do not change any secondary files on disk, only the main workflow
file.

## App Versioning within the SBG eco-system

If you are editing apps that make references to apps in the SBG eco-system and you have passed
Benten an API profile to communicate with the platform, Benten will allow you to change the
version of the App using a drop down. Hand edits to a versioned nested app will be overridden
if the app version is later changed. 

If you hand edit a nested app which is marked as an an SBG app, the id will get a 
change the `id` of the app so it no longer appears to have been uploaded to the SBG system.

**You can turn off all these features by typing `not-sbg-app` in the command bar.**



## Saving to disk
By default Benten will only save the main file to disk when asked to and will only
reload a file from disk when asked to. The configuration file can be edited to
change this behavior such that all changes are live: edits made in Benten are 
saved to disk automatically and edits made to the file outside of Benten are
reloaded automatically.


## Conservation of raw text
All programmatic Benten operations (e.g. dropping steps onto the workflow, 
adding I/O) honor the existing style the user has chosen for a section. e.g.
if the user has chosen to start the `steps` section as a list, dropping new
steps into the workflow will add them as a list.


# Configuration and log files

Configuration files are found under `$XDG_CONFIG_HOME/sevenbridges/benten/`
(If `$XDG_CONFIG_HOME` is not set, `$HOME/.config/sevenbridges/benten/` is used)

Log files are found under `$XDG_DATA_HOME/sevenbridges/benten/`
(If not set, `$HOME/.local/share/sevenbridges/benten/` is used)

# Options (and configuration file)

copy port docs:  If set true then when a workflow input/output port is attached for the first time
                 to a step port, the port documentation will be copied over



# Limitations
YAML allows you to use a `flow style` which is very concise. If you put the top level
elements (`cwlVersion` etc.) in flow style _Benten_ will not work for you. If you
put `step` elements in flow style, _Benten_ will not work for you.


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
