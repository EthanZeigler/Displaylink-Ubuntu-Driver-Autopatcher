#!/usr/bin/env python3

import sys
import tempfile
import shutil
import os
import fnmatch
import subprocess
from pathlib import Path


def find(pattern, path):
    result: list[str] = []
    for root, dirs, files in os.walk(path):
        for name in files:
            if fnmatch.fnmatch(name, pattern):
                result.append(os.path.join(root, name))
    return result

def abort(msg: str, del_tmp=True):
    print("!> Aborting: " + msg)
    if del_tmp:
        shutil.rmtree(tmp_dir)
    sys.exit(1)

# Explaination of what's going on here can be found in the README
if __name__ == '__main__':
    if os.geteuid() != 0:
        abort("This script must be run with sudo", del_tmp=False)

    if len(sys.argv) < 2:
        abort("Missing argument to `DisplayLink USB Graphics Software for UbuntuX.X-EXE.zip`", del_tmp=False)

    tmp_dir = tempfile.mkdtemp()

    print(f"-> Creating tmp directory at `{tmp_dir}`")

    shutil.unpack_archive(sys.argv[1], tmp_dir)
    os.chdir(tmp_dir)

    print("-> Setting installer package as executable")
    installer_package = find('*.run', '.')[0]
    os.chmod(installer_package, 777)

    print("-> Decompressing installer via --noexec --keep")
    if subprocess.call([installer_package, "--noexec", "--keep"]) != 0:
        abort(f"Failed to run `{installer_package} --noexec --keep`")
        
    bad_evdi_tarball = find("evdi.tar.gz", ".")[0]

    print("-> Cloning latest evdi devel version")
    if subprocess.call(["git", "clone", "-b", "devel", "https://github.com/DisplayLink/evdi.git"]) != 0:
        abort("Git clone of evdi failed")

    print("-> Replacing outdated evdi tarball")
    shutil.make_archive("evdi", "gztar", "evdi")
    shutil.move("evdi.tar.gz", bad_evdi_tarball)

    print("-> Moving into decompressed assets")
    os.chdir(Path(bad_evdi_tarball).parent)

    print("-> Setting installer script as executable")
    os.chmod("displaylink-installer.sh", 777)

    if input("-> Run uninstaller first? (Y/n): ") != "n":
        print("-> Running uninstaller to clean up whatever old mess there is")
        subprocess.call(["./displaylink-installer.sh", "noreboot", "uninstall"])

    print("-> Running installer and praying to the linux gods")
    subprocess.call(["./displaylink-installer.sh", "noreboot", "install"])

    if input("-> Clean up temp directory? (Y/n): ") != "n":
        shutil.rmtree(tmp_dir)
    else:
        Path(tmp_dir).chmod(755)
        print(f"-> Temp directory at `{tmp_dir}` left alone")

    print("-> Done")