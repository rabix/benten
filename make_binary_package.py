import os
import shutil
import subprocess
import benten.version
import tarfile
import sys

if not os.path.exists(os.path.join("venv", "bin", "python")):
    try:
        subprocess.run(["python3", "-m", "venv", "venv"])
    except:
        subprocess.run(["python", "-m", "venv", "venv"])

if sys.platform == "win32":
    bindir = "Scripts"
else:
    bindir = "bin"

if not os.path.exists(os.path.join("venv", bindir, "pyinstaller")):
    subprocess.run([os.path.join("venv", bindir, "pip"), "install", "pyinstaller==4.0"])

subprocess.run([os.path.join("venv", bindir, "pip"), "install", "."])
subprocess.run([os.path.join("venv", bindir, "pyinstaller"), "-y", "benten-ls.spec"])
os.chdir("dist")
pkg = benten.version.binary_package_name
shutil.rmtree(pkg, ignore_errors=True)
os.rename("benten", pkg)

tar = tarfile.open(pkg+".tar.gz", "w:gz")
tar.add(pkg)
tar.close()
