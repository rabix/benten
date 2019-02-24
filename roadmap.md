# _Benten_ roadmap

Feb 2019
- [x] Maintain proper editor state on refresh
- [x] Configuration file (Use `$XDG_CONFIG_HOME`)
- [x] File saving/reloading from disk (incl. warnings)
- [x] Refactor of YAML load
- [ ] Refactor workflow for new YAML load
- [ ] SBG versioning system integration
  - [ ] Menu option to select context
  - [ ] Push apps
  - [ ] Change app version (requires pull and clean)
    - [ ] Right click context menu on workflow map to select versions
    - [ ] Menu action to select options
  - [ ] Two flavors of mass updates
  - [ ] Work out background operations
  - [ ] Work out secrets for CI testing
  
March 2019
- [ ] Command bar (is back on!)
  - [ ] Make lower pane tabbed = CMD + Conn
  - [ ] CMD pane = command bar + log/history window
- [ ] Implement editing operations!
- [ ] Error gutter (modify breakpoint gutter for this)
- [ ] Expose menus for editor
- [ ] Expressions!!
 - [ ] job.yaml facility
   - [ ] default job.yaml creation from schema
 - [ ] Editor pane replaced by expression pane (modal, prevents editing anywhere else until saved)
   - [ ] Three panes: expression editor, result, job.yml

April 2019
- [ ] CWL syntax highlighting
- [ ] CWL code completion (probably need to write a parser)
- [ ] Highlight and evaluate an expression (expects an input.yaml)
- [ ] Invoke cwl-runner from command bar
