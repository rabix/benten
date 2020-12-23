import os
import tarfile
from benten.version import __version__

os.chdir("dist")
tar = tarfile.open("benten-ls.tar.gz", "w:gz")
tar.add(f"benten-{__version__}")
tar.close()
