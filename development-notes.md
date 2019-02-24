# Developer notes

## Operations a user should be able to do

- Go to the line of a step
- Add a step/remove a step
- Open the step document (inline or linked)
- List all connections between a pair of nodes, in to/out of a node
- Goto the definition for a connection
- Add a connection/remove a connection





## QT and asyncio

https://docs.python.org/3/library/asyncio-eventloop.html#executing-code-in-thread-or-process-pools

https://doc.qt.io/archives/qq/qq27-responsive-guis.html

## Evaluating JS

https://doc.qt.io/qt-5/qjsengine.html#details


## Travis CI keeping secrets

https://docs.travis-ci.com/user/encrypting-files/


## Sources for test workflows

https://github.com/genome/analysis-workflows


## Edit notification flow

```
if document is loaded into tab
    if document fragment
        inherits document saved attribute
    else:
        set saved text as loaded text

if document edited:
    re-parse document
    
```


## Manual edits to the CWL
These are straightforward
```
if text_changed:
    if on_timer or on_save:
        if valid_yaml:
            if valid_cwl:
                update_internal_representations
            else:
                make_list_of_errors_with_line_numbers_available
                update_internal_representations_as_possible
        else:
            convey_error_to_user_with_useful_detail
```

## Programmatic edits
The edits themselves are straightforward, what is problematic is how to make this work well with
the editor history. However from a hint [here][hist] it looks like a `selectAll` followed by an
`insert` 

[hist]: https://www.qtcentre.org/threads/43268-Setting-Text-in-QPlainTextEdit-without-Clearing-Undo-Redo-History
```
if programmatic_edit:
    doc = plainTextEdit.document()
    curs = QTextCursor(doc)
    curs.select(QTextCursor::Document)
    curs.insertText(new_cwl)
    trigger_text_changed
```
(We basically funnel the programmatic edit into the code editor and activate that mechanism)

## Command bar operation
The command bar operation is translated to a programmatic edit.

## Canvas operation
A canvas operation is translated to a command and goes through that mechanism.


## Cached parsing
At the start we will parse the CWL fresh for each change. For physically large CWLs this 
can slow things down (because of Ruamel's speed). When this starts to be a problem we have to
consider if we can cache the results and just process the diffs. But this will make the software
more complex. 


## SBG Ecosystem specific features

If the `id:` of a step's `run` component points to a SBG app 
(e.g. `id: admin/sbg-public-data/salmon-quant-reads-0-9-1/11`)
then Benten will offer the ability to switch that step to any available version. In the workflow
map the node will show the version number of the App.


## Synchronization of edits (nested inline steps) and step interface reparsing (inline or external)

The ability to open sub workflows in new benten editor panes raises the interesting challenge of how
to keep things consistent between the windows when edits happen. This is especially involved
when the steps are nested inline steps.

We have the two following cases

1. One or more tabs refer to sub-workflows inlined in the same document
2. We have a workflow which is an external file
 

### Inline in the same document

In this case edits in different tabs are reflected in the same underlying document in the editor
and each tab keeps track of the "path" required to get to the step relative to the original
document. These changes are propagated simultaneously to the raw text of each tab and the document
is reparsed when we activate a tab. These tabs have a sibling relationship despite the fact that
they may have been initially opened in a hierarchical fashion.
If a node is edited out of the document, that editor tab is closed.

Note that this underlying document does not have to be the original document we opened. These
tabs could result from opening inlined steps in a sub-workflow

### External steps

Edits to an external sub-workflow opened in a tab do not affect the content of the parent, but
the interface might have changed, which is important for auto-completion etc. For this reason
we keep track of the parent of an external sub-workflow and trigger a reparse when the workflow
is modified. This does not need to recurse up - only one level of computation is needed.


### No duplicate tabs
The multi-document manager keeps track of the document url and internal path (for inlined steps)
for all open documents. If the user attempts to open a duplicate document, the user is switched
to the existing tab. As needed an newly opened document is marked as a sibling (for inlined steps)
of existing tabs, so their synchronization can be consistent.


### Corner case - close sub-workflow with inline steps that are opened in another tab 
Say our main workflow A has a sub-workflow B, which we open in a new tab. B has an inline
step C. Now we close B. Then we open B again. How do we ensure that B and C are still linked?

The code that manages our inline steps will keep track of the file path of the underlying
document, so that if it is opened up in a tab, it automatically gets correctly positioned
as a sibling document!


### Closing tabs
All but the base (originally opened, first) tab can be closed. This is based on the philosophy
that one Benten editor instance is for one workflow and its children.


## Some design decisions

### graph Layout
The "dot" layout (topsort, hierarchical) does well, but becomes cluttered when we have all our
individual input and output nodes listed out. I find that by collapsing all input and output
into one common entry and exit node respectively, the layout looks a lot neater! The next thing
to change is 

### Can we embed a 'professional' editor somehow?

https://github.com/pyzo/pyzo/tree/master/pyzo/codeeditor

https://qutepart.readthedocs.io/en/latest/#

https://pypi.org/project/pyqode.core/2.1.0/

https://github.com/tucnak/novile

https://www.riverbankcomputing.com/software/qscintilla/download


### Do we NEED Ruamel.yaml ?
Granted I'm doing interactive testing with the worst possible file (`salmon.cwl`) which weighs in
at 151 kB (!) a lot of SBG workflows are like this because they are compacted into one file and
have a ton of documentation.

However the Ruamel loading delay is a little jarring. I'm not bothering testing it with smaller
handwritten files because I want to see how far we can push this.

For our purposes what we need to do is

1. For a given YAML key, find the line it is on (scroll editor to step/node/component)
2. For a given YAML entry in a list or map find the last line for that entry (insert a programmatic edit there)
3. For a given YAML entry find the range of lines of the whole section (to delete or replace that section) 

Given the structured nature of YAML and CWL might we be able to come up with a fast algorithm that
finds the appropriate line for scrolling, inserting or deleting? Then we can use PyYamls fast C loader
to load and parse the CWL or even just incrementally update the structure based on the edits.

For now (02.02.2019) I will ignore this issue for a few weeks while I implement some key functionality.
Then we will revisit.

02.04.2019 - Yes! We can sub-class the CSafeLoader to add line numbers for the start and end of the
block! There is no appreciable drop in efficiency of the parsing!


## ruamel YAML loading stats

For `ruamel.yaml 0.15.51`
```
%timeit ruamel.yaml.load(open("salmon.cwl", "r").read
   ...: (), Loader=ruamel.yaml.RoundTripLoader)
1.21 s ± 162 ms per loop (mean ± std. dev. of 7 runs, 1 loop each)
```

For `ruamel.yaml 0.15.85`
```
%timeit ruamel.yaml.load(open("salmon.cwl", "r").read
   ...: (), Loader=ruamel.yaml.RoundTripLoader)
715 ms ± 19.4 ms per loop (mean ± std. dev. of 7 runs, 1 loop each)
```
