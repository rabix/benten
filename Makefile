SERVER_VERSION=$(shell python -c 'import benten.version ; print(benten.version.__version__)')
CLIENT_VERSION=$(shell node -e 'pkg=require("./vscode-client/package.json"); console.log(pkg.version);')
PKG = $(shell node -e 'console.log(`benten_$(SERVER_VERSION)_$${process.platform}_$${process.arch}`);')

dist-pkg: dist/$(PKG).tar.gz vscode-client/benten-cwl-$(CLIENT_VERSION).vsix
	@echo Done building dist/$(PKG).tar.gz and vscode-client/benten-cwl-$(CLIENT_VERSION).vsix

checkversion:
	echo "Server and client should be the same version.  If they don't match, update the version files."
	@echo Server version in benten/version.py is "$(SERVER_VERSION)"
	@echo Client version in vscode-client/package.json is "$(CLIENT_VERSION)"
	test "$(SERVER_VERSION)" = "$(CLIENT_VERSION)"

dist/$(PKG).tar.gz: venv checkversion
	venv/bin/pip install .
	venv/bin/pyinstaller -y benten-ls.spec
	cd dist && \
	rm -rf $(PKG) && \
	mv benten $(PKG) && \
	tar czf $(PKG).tar.gz $(PKG)

venv:
	python3 -m venv venv
	venv/bin/pip install pyinstaller==4.0

vscode-client/benten-cwl-$(CLIENT_VERSION).vsix: checkversion
	cd vscode-client && \
	npm install && \
	node_modules/.bin/vsce package

clean:
	rm -rf build dist

reallyclean: clean
	rm -rf venv
