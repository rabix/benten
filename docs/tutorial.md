<!-- TOC -->

- [General Tutorial](#general-tutorial)
    - [Starting out](#starting-out)
    - [Autocomplete](#autocomplete)
    - [Navigation](#navigation)
        - [Navigation bar](#navigation-bar)
        - [Workflow map](#workflow-map)
    - [Command line](#command-line)
    - [Scaffolding](#scaffolding)
- [Suggested git based workflow](#suggested-git-based-workflow)
- [SBG Tutorial](#sbg-tutorial)
    - [Credentials file and profiles](#credentials-file-and-profiles)
        - [Switching contexts while editing](#switching-contexts-while-editing)
    - [Push an App to the platform](#push-an-app-to-the-platform)
        - [Pushing inlined apps.](#pushing-inlined-apps)
        - [Editing an app after pushing](#editing-an-app-after-pushing)
        - ["sbg:id"](#sbgid)
    - [Run a test](#run-a-test)
    - [Re-run a test](#re-run-a-test)
    - [Upgrade/downgrade apps](#upgradedowngrade-apps)
        - [Inlined apps: Upgrade/downgrade inlined apps in workflows](#inlined-apps-upgradedowngrade-inlined-apps-in-workflows)
    - [Update all](#update-all)
        - [Note on the raw code in the SBG repository](#note-on-the-raw-code-in-the-sbg-repository)
    - ["Forking" an inlined app](#forking-an-inlined-app)
- [Appendix](#appendix)
    - [Configuration and log files](#configuration-and-log-files)
        - [Configuration](#configuration)
        - [Logs and other user data](#logs-and-other-user-data)
    - [Sample credentials file with all SBG platforms](#sample-credentials-file-with-all-sbg-platforms)
    - [Experimental feature: Editing inlined steps](#experimental-feature-editing-inlined-steps)
        - [Quirks](#quirks)
    - [Limitations/Quirks](#limitationsquirks)
        - [YAML flowstyle](#yaml-flowstyle)
        - [Synchronized editing and undo/redo](#synchronized-editing-and-undoredo)
        - [Inline step editing and blank lines](#inline-step-editing-and-blank-lines)
        - [Opening CWL in JSON format](#opening-cwl-in-json-format)
        - [Modifying autocomplete templates](#modifying-autocomplete-templates)
        - [Editor options](#editor-options)
    - [A note on the modular nature of CWL](#a-note-on-the-modular-nature-of-cwl)
        - [To inline or not to inline](#to-inline-or-not-to-inline)
            - [Use cases for in-lining](#use-cases-for-in-lining)
            - [Use cases for linking](#use-cases-for-linking)

<!-- /TOC -->

# General Tutorial

We will create a nested workflow with a mixture of inline and linked steps to
demonstrate most of the common features of _Benten_. In the end you should end
up with a set of nested workflows that look like this: 

```
WF1 = (IN)-->(C)-->(WF2)-->(WF3)-->(OUT)

WF2 = (IN)-->(E)-->[WF3]-->(OUT)

WF3 = (IN)-->[C]-->(C)-->(OUT)
```

Where
```
(C) = CommandLineTool, inlined
[C] = CommandLineTool, linked
(E) = ExpressionTool, inlined
(WF) = Workflow, inlined
[WF] = Workflow, linked
```

## Starting out

`WF1 = (IN)-->(C)-->(WF2)-->(WF3)-->(OUT)`

Navigate to a scratch directory where you can create files for the tutorial.

Open up an instance of _Benten_ from the terminal with the name of the
workflow we want to create:

```benten wf1.cwl -v
```

Since `wf1.cwl` does not exist, _Benten_ will create an empty document. 
The `-v` flag simply turns on debugging messages and is not really needed, 
but is helpful if you run into an issue and 
want to [report it](https://github.com/rabix/benten/issues)

## Autocomplete

Several CWL constructs are available as code auto-completions. Once you begin
typing these completions will be made available to you. The completions are
stored in the file `snippets.yaml` in the _Benten_ configuration directory in
an easy to understand format.

Since we decided to start out with a workflow, either manually type in a 
workflow or use the workflow template snippet.

## Navigation

As soon as Benten realizes this document is a workflow, it will open a second
pane and display a map of the workflow.




### Navigation bar

### Workflow map



## Command line

Now you can either start typing in code yourself or get a little assist from
the editor. Switch to the command line by either clicking on it or pressing
`CMD + p` on macOS / `CTRL + p` on Linux/Windows.
You can type `?` to get help on the commands available.

## Scaffolding

In our case we will use the `create wf` command to create a scaffold for a workflow.

You should see that the view changes to accommodate the workflow map, which
we will use to help us navigate.

Now you can continue to edit by hand, but here we will use a little assist to
add an empty inline step, corresponding to the first `CommandLineTool` component.

Type `new step1`. This should append a new step to the document inline and the
step's contents should be empty. In the workflow map you should see this new
step appear in between the `Input` and `Output` nodes. It should indicate that
there is an issue with the node. This is fine - we haven't defined what the
node is with any code yet.


Let's flesh out the Command Line Tool.





# Suggested git based workflow

In order to maintain maximum flexibility - allowing you to change versions of
tools and workflows in a manner not affecting other users, it is best to




# SBG Tutorial

_Benten_ has some handy commands/features that help integrate your development
flow with the SBG powered platforms such as [CGC], [CAVATICA], [Fair4Cures].

[CGC]: https://cgc.sbgenomics.com
[CAVATICA]: https://cavatica.sbgenomics.com
[Fair4Cures]: http://f4c.sbgenomics.com/

## Credentials file and profiles

_Benten_ will look over your Seven Bridges API credentials file 
(`~/.sevenbridges/credentials`), if you have one, and list all 
your profiles on a "Contexts" menu. This menu allows you to select
a context that you can push (and pull) apps to. 

If you use the SBG API you already have an API configuration file. If not, you
should create one. It is usually located in `~/.sevenbridges/credentials` but
_Benten_ allows you to configure this by setting the path in the 
main configuration file.

Briefly, each section in the SBG configuration file (e.g. `[cgc]`) is a profile 
name and has two entries. The end-point and an authentication token, which 
you get from your developer tab on the platform.

```
[cgc]
api_endpoint = https://cgc-api.sbgenomics.com/v2
auth_token   = 282174488599599500573849980909
```

You can have several profiles on the same platform if, for example, you are an
enterprise user and you belong to several divisions. Please refer to the API
documentation for more detail.

**The credential file is only parsed when _Benten_ is opened. If you change 
your credential file you have to close and re-open _Benten_ for the changes 
to take effect**

### Switching contexts while editing

Say you are editing a workflow in the context of your "CGC" profile, and 
you switch to your "Cavatica" profile, where the current app and the nested 
apps are not present. When you go to push your app, _Benten_ will discover 
that the orginal project does not exist (probably). If so you will then get
a "Push dialog" that you got when originally pushing the app and you will have 
to fill out the destination project and app id. Benten will then proceed to 
install this app in that project on Cavatica. However, now you will no longer 
be able to change the versions of the subworkflows since this history does 
not exist in the Cavatica repository. The workflow will work exactly the same
however. 

Typically, if you work in multiple contexts (which is very rare), it is most 
convenient to develop on just one platform, and then distribute the final 
frozen workflows to collaborators on other platforms.

## Push an App to the platform
Type `sbpush <message>` in the _Benten_ command line to push the current App 
to the  current SBG platform. If this is the first time you are pushing the 
App you will have to supply a project and app name. 
`sbpush <message> project/appid`.

### Pushing inlined apps.
The push command applies to the current app being edited. If this is an inlined
app, just that app is pushed. This naturally marks all parent apps as edited if 
they are registered in an SBG repository. 


### Editing an app after pushing
Pushing an app to the SBG platform registers it. Pushing an app will change one
line in your local copy - the app id field. This will be replaced with the app
id string the SBG repository returns. Once you begin to edit the app the suffix
`-local-edits` will be added to the id to indicate this.

### "sbg:id"
The SBG platform uses the "sbg:id" field to track versions and links across apps 
used in workflows. Hand editing this can result in problems with app management
(such as upgrading/downgrading versions) 

## Run a test
After pushing an app typing `sbrun` will create a draft task on the platform
and open a browser window at the draft task. You can also type `sbrun` directly
and this will push the app and create a draft task in one go. The task-id of
the created task is saved in a file called `<cwl-name>.sbg.job.txt`. Typing
`sbrun?` will retrieve the status of the task and print it in the console.

## Re-run a test
Typing `sbrun` subsequent times will clone the task, which means that your
previous inputs will be preserved in the new draft task. Typing `sbrun!` will
skip the draft task stage and directly run the cloned task. 

## Upgrade/downgrade apps
If an app is registered with the SBG tool repository, the typing `revisions`
will return a list of revisions for the app. Typing `pull-revision <N>`, where
`N` is a valid revision number, will retrieve the code for that version from
the SBG repository and replace it.

### Inlined apps: Upgrade/downgrade inlined apps in workflows
The `revisions` and `pull-revision` commands operate on the App you are 
currently viewing. **If you are viewing an inline App in a workflow you will
be able to upgrade or downgrade just that App**. Note that this will cause all
parent apps to be marked as edited, because they are now changed.

## Update all
The `update-all` command will cause all inlined apps to be recursively updated
to their latest version. This operation has some subtle points: if an inlined
app has a newer revision it will be updated to that new revision and 
*the operation will not recurse further for that app*. If an inlined app is
already at the latest version, the operation will recurse further until it
finds a child app that has updates, and will update that.
**This operation can take a while, depending on how many nested workflows there are**

### Note on the raw code in the SBG repository
Currently (Q2 2019) the SBG repository stores the CWL code in JSON format.
For this reason, if you pull code back from the SBG repository it will arrive
in the editor as a YAML conversion of the JSON. The YAML conversion will
keep the top level fields in the order found in the CWL templates, but the
inner fields will in arbitrary order. In short, the raw code will not be 
preserved if you ever pull code back from the SBG repository.

## "Forking" an inlined app
If you edit an inlined app, don't push it's changes but push the main app
you will have created a "fork", in a sense, of the inlined app. This app
is disconnected from the SBG repository and the SBG app management system
will not realize it is (or was) in the SBG app repository. When you `sbpush`
this "forked" app it will create a new revision of the original app "merging"
it back into the repository.

# Appendix

## Configuration and log files

### Configuration
The configuration file is found under `$XDG_CONFIG_HOME/sevenbridges/benten/config.ini`
(If `$XDG_CONFIG_HOME` is not set, `$HOME/.config/sevenbridges/benten/` is used)

On first startup benten will create a default configuration file for you. The configuration
file is in the `.ini` format and is fairly self-explanatory. The default file can be
found [here](https://github.com/rabix/benten/tree/master/benten/000.package.data/config.ini)

### Logs and other user data
Log files are found under `$XDG_DATA_HOME/sevenbridges/benten/`
(If not set, `$HOME/.local/share/sevenbridges/benten/` is used)


## Sample credentials file with all SBG platforms

```
[sbg-us]
api_endpoint = https://api.sbgenomics.com/v2
auth_token   = 671998030559713968361666935769

[sbg-eu]
api_endpoint = https://eu-api.sbgenomics.com/v2
auth_token   = 115756986668303657898962467957

[sbg-china]
api_endpoint = https://api.sevenbridges.cn/v2
auth_token   = 362736035870515331128527330659

[cgc]
api_endpoint = https://cgc-api.sbgenomics.com/v2
auth_token   = 282174488599599500573849980909

[cavatica]
api_endpoint = https://cavatica-api.sbgenomics.com/v2
auth_token   = 521419622856657689423872613771

[f4c]
api_endpoint = https://f4c-api.sbgenomics.com/v2
auth_token   = 590872612825179551336102196593
```

## Experimental feature: Editing inlined steps

**This feature is experimental. It basically works, but the edit history 
(ubdo/redo stack) is disrupted.** 

By setting the `allow_inline_editing` option to `True` you can enable editing
of inlined steps in a new tab just as you would edit linked steps - by double
clicking on the node.

```
[editor]
type_burst_window = 0.5
allow_inline_editing = True # <----------
```

If you edit an inlined step in a new tab, these edits will be propagated 
to all the related views just as if you had edited the original (base) document.


### Quirks
- The command history for the document is lost


## Limitations/Quirks

### YAML flowstyle
YAML allows you to use a `flow style` which is very concise. If you put the top level
elements (`cwlVersion`, `class`, `steps` etc.) in flow style _Benten_ will not work for you.
If you put the elements in the `step` field in flow style, _Benten_ will not work for you.

### Synchronized editing and undo/redo
When you edit a view of a document (parent or child) your edits are propagated to all the views.
However, except in the view where you made the original edit, the edit is created as an edit of the
whole document. For this reason you'll lose your cursor place after an undo/redo. Also, this
undo/redo registers as a new edit in the linked views. *In general, it is most comfortable to edit
an inlined sub-workflow in it's own view.*

### Inline step editing and blank lines
If you have an inline step, and have a blank line with white-spaces, on editing the step these
white-spaces will disappear from your blank line. In general it is a good practice not to have
spurious whitespace in a blank line anyway ...

### Opening CWL in JSON format
If passed a CWL in JSON format _Benten_ will convert it to YAML, save this conversion as a file
called `<original file>.cwl`. If the original workflows have linked
subworkflows that are in JSON, they can be opened in the same manner, but edits will go to the
converted file, which is not the one linked from the workflow.

Basically, if you are using _Benten_ presumably you do a lot of CWL coding by hand, and it's very
likely you are doing this in YAML, not JSON, so the best flow is to just stay in YAML. **This
auto-conversion is offered as a convenience when you just want to peek at a CWL in JSON format,
not for doing regular work in hand written JSON (shudder).**

### Modifying autocomplete templates

The CWL templates are found in the `snippets.yaml` file and can be customized.

### Editor options
The editor options (section `[editor]`) are passed verbatim to the Ace editor.
So you can use [whatever is allowed](https://github.com/ajaxorg/ace/wiki/Configuring-Ace)
There are a few options you can not mess with, and these are over ridden.
For example tabs are disabled - YAML does not allow tabs, it uses spaces.
Also, tab spacing is fixed at 2 spaces, because that is the only correct answer.


## A note on the modular nature of CWL

CWL has a very useful feature in that any CWL document (representing a unit of
action) can be included in any CWL workflow as a step. In this manner CWL 
workflows can be built up modularly from a library of tools, with workflows
combining and nesting this library very elegantly to any depth needed.

CWL allows you to either link to an external CWL document by reference (much 
like an `include` or `import` statement in some languages) or to directly 
include the code inline in the main document.

### To inline or not to inline

#### Use cases for in-lining
- You want to freeze all components of the workflow for reproducibility purposes
- You want to share the complete CWL in a self contained form
- You want to modify a sub-workflow without affecting other workflows that use
  that step.
  

#### Use cases for linking
- You want to keep the parent workflow compact and easier to understand. You are
  confident that changes to the linked documents are systematic and under control. 
- You want your parent workflow to always reflect the current state of the linked 
  workflows
- You have multiple copies of the same subworkflow in your parent workflow and
  you want to ensure they remain in synch
