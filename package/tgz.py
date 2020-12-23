import os
import tarfile

os.chdir("dist")
tar = tarfile.open("benten-ls.tar.gz", "w:gz")
tar.add("benten")
tar.close()
