import os
import shutil
import subprocess
import benten.version
import tarfile

subprocess.run([os.path.join("venv", "bin", "pip"), "install", "."])
subprocess.run([os.path.join("venv", "bin", "pyinstaller"), "-y", "benten-ls.spec"])
os.chdir("dist")
pkg = benten.version.binary_package_name
shutil.rmtree(pkg, ignore_errors=True)
os.rename("benten", pkg)

tar = tarfile.open(pkg+".tar.gz", "w:gz")
tar.add(pkg)
tar.close()
