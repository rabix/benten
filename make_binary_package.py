import os
import shutil
import subprocess
import benten.version
import tarfile

if not os.path.exists(os.path.join("venv", "bin", "python")):
    subprocess.run(["python3", "-m", "venv", "venv"])

if not os.path.exists(os.path.join("venv", "bin", "pyinstaller")):
    subprocess.run([os.path.join("venv", "bin", "pip"), "install", "pyinstaller==4.0"])

subprocess.run([os.path.join("venv", "bin", "pip"), "install", "."])
subprocess.run([os.path.join("venv", "bin", "pyinstaller"), "-y", "benten-ls.spec"])
os.chdir("dist")
pkg = benten.version.binary_package_name
shutil.rmtree(pkg, ignore_errors=True)
os.rename("benten", pkg)

tar = tarfile.open(pkg+".tar.gz", "w:gz")
tar.add(pkg)
tar.close()
