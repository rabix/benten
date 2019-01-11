To your `.vimrc` you should add the following sections (if you haven't already)


Register CWL 
```
au BufNewFile,BufRead *.cwl setlocal ft=cwl
```

(You can check if this works properly by loading a `cwl` file and executing `:set ft?`. Verify that 
it returns `filetype=cwl`)





`:PlugStatus` - check if the plugin took.

I had to manually do `:PlugInstall "etc."` for the plugins on my setup


Register the language server for vim:

```
if executable('benten-ls')
    au User lsp_setup call lsp#register_server({
        \ 'name': 'cwl',
        \ 'cmd': {server_info->['benten-ls']},
        \ 'whitelist': ['cwl'],
        \ })
endif
```

Once all this is cleared, you can should load up a CWL file and verify the vim language client
AND the CWL language server is running by doing `:LspStatus` which should return 
`cwl: starting` and then `cwl: running`


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