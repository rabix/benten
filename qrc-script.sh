#!/bin/sh
# This script is here to help create the .qrc file we need for bundling
# the Ace editor javascript libraries for use with QWebEngineView
# If only .qrc allowed directory includes ...

QRC=./benten.qrc
ACE_DIR=./benten/gui/ace/ace-builds/src-min-noconflict
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

echo '  </qresource>' >> ${QRC}
#echo '  <qresource>' >> ${QRC}
#echo '      <file>benten/gui/benten-icon.png</file>' >> ${QRC}
#echo '  </qresource>' >> ${QRC}
echo '</RCC>' >> ${QRC}

pyside2-rcc benten.qrc -o benten/gui/ace/qtresources.py
