# Benten
_(This software is in the planning stage)_

This is a [Language server](https://microsoft.github.io/language-server-protocol/) and 
workflow helper for the [Common Workflow Language](https://www.commonwl.org/) written in Python.

Many advanced CWL users are comfortable creating tools and workflows "by hand"
using a plain text editor. When creating complex enough workflows there are some 
activities that can get tedious, repetitive and error prone when done manually. 
_Benten_ is a GUI that automates and simplifies some of these tasks. 
_Benten Language Server_ is a language server for the Common Workflow Language that 
supplies autocomplete functionality (List of [tools] that support LSP).

[tools]: https://microsoft.github.io/language-server-protocol/implementors/tools/


[![Tests](https://travis-ci.com/rabix/benten.svg?branch=master)](https://travis-ci.com/rabix/benten)
[![codecov](https://codecov.io/gh/rabix/benten/branch/master/graph/badge.svg)](https://codecov.io/gh/rabix/benten)

# Workflow helper component

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

Clicking on the input or output node will show all the inputs/output connections
of the workflow on the connection table.

Double-Clicking on a step will switch the View to show this step. 

A breadcrumb trail above the View keeps the user oriented. Clicking on a breadcrumb
switches to the View to that step.

If a step is a subworkflow refering to another file, this is just like having 
different files open in different editor instances. If the step is inline, then 
edits in the different views are actually edits to the same file. 

In such a case edit history operates a little specially. In the view where an
edit is done, a normal history of edits evolves. In the other views a squashed
edit is applied when switching to that view, so the history is less rich.

Selecting multiple steps enables the option to `implode` these steps into a
subworkflow. You will be asked for a file path to save the new step into. 
Leaving it blank creates an inline step. 

Choosing `extract`, instead, on one or more steps will pack this code into a 
separate process object (`Workflow`, `CommandLineTool` etc.) in a file you choose.

Selecting a step and asking for `inline` will copy all the code into the main
workflow file if the step refers to an external file.

## Breadcrumb trail

As mentioned earlier, Views can switch to displaying a step within the current 
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
```

Note that undo and redo operations do not change any secondary files on disk, only the main workflow
file.

 
## 4 way synchronization 
By default Benten will only save the main file to disk when asked to and will only
reload a file from disk when asked to. The configuration file can be edited to
change this behavior such that all changes are live: edits made in Benten are 
saved to disk automatically and edits made to the file outside of Benten are
reloaded automatically.


## Conservation of raw text
To the extent that `ruamel.yaml` preserves the orginal layout of a YAML file
Benten will conserve the raw text the developer types in. CWL allows users to
represent a set of objects (steps, ports etc.) as either lists or maps. 
All programmatic Benten operations (e.g. dropping steps onto the workflow, 
adding I/O) honor the existing style the user has chosen for a section. e.g.
if the user has chosen to start the `steps` section as a list, dropping new
steps into the workflow will add them as a list.



# Language server component


## Proposed Features
- Auto completion of step and port names
- On demand insertion of CWL section templates (process objects, inputs, outputs, steps)
- CWL Syntax checking and error notifcations
- Refactoring of CWL documents
  - Renaming workflow components (input ids, step ids)
  - Imploding of a set of workflow steps into a subworkflow
  - Exporting of individual steps or groups of steps into external workflow documents
  - Opening of subworkflows in new editor tabs
- For editors that support it, a diagram pane
  - The pane shows a graphical depiction of the workflow
  - The pane allows dropping on local CWL files onto the workflow, to be added as steps

## Testing with vim
Currently (2019.01) the server is under development and it doesn't do anything useful. 
[Here's how I'm testing it with `vim`](vim/Readme.md).


# Configuration and log files
All configuration and log files are found under `${HOME}/.sevenbridges/benten/`

Benten language server's log file is `benten-ls.log`

CWL templates used for autocomplete are found under `cwl-templates`. Default templates are supplied
and they can be edited and personalized.


# License
Apache 2.0

# Thanks
- [The Sourcegraph Python language server][src-pyls] source code. Some components have been used
  with light modification and some have been studied to understand the Language Server Protocol

[src-pyls]: https://github.com/sourcegraph/python-langserver


# What's in a name? 

**Saraswati** is the Hindu goddess of learning and knowledge and a long time ago 
she visited Japan, where she is known as [Benzaiten] (**Benten** for short) and 
her sitar has morphed into a Japanese lute but she has kept some of her many arms.

Benzaiten is the goddess of everything that flows: water, time, words, speech, 
eloquence, music and by extension, knowledge. Therefore _Benten_ is an 
appropriate goddess for scientific workflow developers.

[Benzaiten]: https://en.wikipedia.org/wiki/Benzaiten 
