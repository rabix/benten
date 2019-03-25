#!/bin/sh
# This script is here to help create the .qrc file we need for bundling
# the Ace editor javascript libraries for use with QWebEngineView
# If only .qrc allowed directory includes ...
pushd ./ace-editor/

QRC=ace.qrc
ACE_DIR=./ace-builds/src-min-noconflict

echo '<!DOCTYPE RCC>' > ${QRC}
echo '<RCC version="1.0">' >> ${QRC}
echo '  <qresource>' >> ${QRC}

# Each file in the Ace source folder has to be added in individually
for a in $(find ${ACE_DIR} -d)
do
    # if this is not a folder
    if [ ! -d "$a" ]; then
        echo '      <file>'$a'</file>' >> ${QRC}
    fi
done

echo '    <file>cwl_snippets.js</file>' >> ${QRC}
echo '  </qresource>' >> ${QRC}
echo '</RCC>' >> ${QRC}

popd
pyside2-rcc ./ace-editor/${QRC} -o ./benten/gui/ace/resources.py
