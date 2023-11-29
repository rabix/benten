# Running Benten with vim 

<img height="400px"
src="https://github.com/denbi/denbi-benten/blob/main/media/2019.10.22/vi-type-hover.png"></img>


## Ensure you have a recent version of VIM

The LSP client plugin requires vim8/neovim. It is best to
have atleast **vim 8.1** which allows several code intelligence
features (auto-complete, error gutter, symbol list etc.) to
work in an intuitive manner out of the box.

## Install a plugin manager

I have found [`vim-plug`](https://github.com/junegunn/vim-plug) to work nicely
with the required plugins. Install is simple following the instructions 
[here](https://github.com/junegunn/vim-plug#installation)

## Modify `.vimrc` file 

Your `.vimrc` file has to be modified to ensure the following

1. Register CWL as a file type
2. Install LSP client for VIM
3. Configure LSP client to run `benten-ls` when it loads up a CWL document

A minimally functional `.vimrc` file is given here (explanations at end)

```
syntax on

au BufNewFile,BufRead *.cwl setlocal ft=cwl

" Specify a directory for plugins
" - For Neovim: ~/.local/share/nvim/plugged
" - Avoid using standard Vim directory names like 'plugin'
call plug#begin('~/.vim/plugged')

" Make sure you use single quotes

Plug 'prabirshrestha/async.vim'
Plug 'prabirshrestha/vim-lsp'
Plug 'prabirshrestha/asyncomplete.vim'
Plug 'prabirshrestha/asyncomplete-lsp.vim'

call plug#end()

inoremap <expr> <Tab> pumvisible() ? "\<C-n>" : "\<Tab>"
inoremap <expr> <S-Tab> pumvisible() ? "\<C-p>" : "\<S-Tab>"
inoremap <expr> <cr> pumvisible() ? "\<C-y>" : "\<cr>"


let g:lsp_log_verbose = 1
let g:lsp_log_file = expand('~/.vim/vim-lsp.log')

if executable('benten-ls')
    au User lsp_setup call lsp#register_server({
        \ 'name': 'cwl',
        \ 'cmd': {server_info->['benten-ls']},
        \ 'whitelist': ['cwl'],
        \ })
endif
```

### Explanation
```
au BufNewFile,BufRead *.cwl setlocal ft=cwl
```
This registers CWL as a type.
(You can check if this works properly by loading a `cwl` file and executing `:set ft?`. Verify that 
it returns `filetype=cwl`)


```
call plug#begin('~/.vim/plugged')
...
call plug#end()
```
Registers plugins. There are often issues in getting plugins to install the 
first time round.

You should check if the plugins are loaded and active by doing `:PlugStatus`
I had to do `:PlugInstall` to ensure the plugins are installed.

*Note:* If you want `CWL` syntax highlighting you can try adding `Plug 'manabuishii/vim-cwl'`
From this project: https://github.com/manabuishii/vim-cwl
This is not necessary for testing.


```
if executable('benten-ls')
    au User lsp_setup call lsp#register_server({
        \ 'name': 'cwl',
        \ 'cmd': {server_info->['benten-ls']},
        \ 'whitelist': ['cwl'],
        \ })
endif
```
This tells `vim` to look for the executable `benten-ls` in the path and start it up as a language
server when it opens a `cwl` file.

## Checking if it works

After doing this you should be able to load up a CWL file and verify the vim language client
AND the CWL language server are running by doing `:LspStatus` which should return 
`cwl: starting` and then `cwl: running`


## Available commands

The available commands are found on the [VIM LSP plugin page][vl-help].

[vl-help]: https://github.com/prabirshrestha/vim-lsp#supported-commands


# Other options

I have not explored this, but [ALE (Asynchronous Lint Engine)](https://github.com/w0rp/ale) also acts as
a language client, and so should also be able to be configured to work with
Benten.
