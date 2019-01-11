# Running Benten with vim 

You will need to (if you haven't already)
1. Register CWL as a file type
2. Install a plugin manager - I use [`vim-plug`](https://github.com/junegunn/vim-plug)
3. Install LSP client for VIM
4. Configure it to run `benten-ls` when it loads up a CWL document

An minimally functional `.vimrc` file (mine) is

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
Registers plugins. I have some issue in getting plugins to install the first time round.

You should check if the plugins are loaded and active by doing `:PlugStatus`
I had to manually do `:PlugInstall "<plugin name>"` for each of the plugins on my setup


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

After doing this you should be able to load up a CWL file and verify the vim language client
AND the CWL language server are running by doing `:LspStatus` which should return 
`cwl: starting` and then `cwl: running`
