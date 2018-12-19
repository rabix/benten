# Benten
_(This software is in the planning stage)_

Language server and workflow helper for the Common Workflow Language

Many advanced CWL users are comfortable creating tools and workflows "by hand"
using a plain text editor. When creating complex enough workflows there are some 
activities that can get tedious, repetitive and error prone when done manually. 
_Benten_ is a CWL workflow helper that gives a little extra assist to users 
developing CWL workflows by hand.

# Proposed Features
- Auto completion of step and port names
- On demand insertion of CWL section templates (process objects, inputs, outputs, steps)
- CWL Syntax checking and error notifcations
- Code folding
- Refactoring of CWL documents
  - Renaming workflow components (input ids, step ids)
  - Imploding of a set of workflow steps into a subworkflow
  - Exporting of individual steps or groups of steps into external workflow documents
  - Opening of subworkflows in new editor tabs
- For editors that support it, a diagram pane
  - The pane shows a graphical depiction of the workflow
  - The pane allows dropping on local CWL files onto the workflow, to be added as steps

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
