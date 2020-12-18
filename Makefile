PKG = $(shell node -e 'pkg=require("./vscode-client/package.json"); console.log(`benten_$${pkg.version}_$${process.platform}_$${process.arch}`);')

dist-pkg: dist/$(PKG).tar.gz

dist/$(PKG).tar.gz: venv
	venv/bin/pip install .
	venv/bin/pyinstaller -y benten-ls.spec
	(cd dist && \
	rm -rf $(PKG) && \
	mv benten $(PKG) && \
	tar czf $(PKG).tar.gz $(PKG) )

venv:
	python3 -m venv venv
	. venv/bin/activate
	venv/bin/pip install pyinstaller==4.0

clean:
	rm -rf venv build dist
