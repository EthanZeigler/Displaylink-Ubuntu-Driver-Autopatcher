# Displaylink Ubuntu Driver Autopatcher

This package makes an attempt to automatically update the evdi package within the
Ubuntu DisplayLink installer by replacing the embedded tarball with the latest
development version from Github. This fixes issues with kernel versions >= 6.6.

Tested on POP_OS 22.04 LTS

### Why?

I spent several days getting these drivers to work with Pop_OS 22.04 and
didn't want anyone else to go through the pain of doing the same

### What does this do?

This python3 script uses some of the embedded fuctionality of the DisplayLink
Ubuntu installer to unpack its contents including the embedded version
of the evdi package which handles virtual desktops. This script then replaces
the evdi tarball with a new one made from cloning the evdi github repository's
`devel` branch. Finally, it runs displaylink's secondary embedded installer script within
the unpacked contents which bypasses integrity checks. That secondary script
is unaware that the evdi tarball isn't original and therefore builds (fingers crossed)
without any additional issues.

### Troubleshooting

#### [old evdi version still sticking around](https://github.com/DisplayLink/evdi/issues/433#issuecomment-1838545456)

#### evdi compilation error: missing python header
Ensure these libraries are installed. `apt install pybind11-dev python3.10-venv python3-pip`.
They're only required by the included python library which really _shouldn't_ be
necessary but sometimes you just make the compiler happy and move on.

#### evdi complation error: drm_gem_prime_fd_to_handle undeclared

The old evdi package is hiding somewhere. I also ran into this but it was a little
too complex for the simple python script.

1. Clone the latest evdi library from github `git clone -b devel https://github.com/DisplayLink/evdi.git`
2. `cd` into it
3. Ensure package is fully removed from dkms. `sudo dkms status` should _not_
list evdi. If it does, remove it with `sudo dkms remove evdi/<whatever-version-is-there> --all`
4. `sudo rm -rf /var/lib/dkms/evdi` for safety in case it still won't leave.
5. Run `sudo dkms add ./modules`. This seems to be more reliable than how the
DisplayLink installer does it via referencing the tarball.
6. Run the autopatcher script again. When it asks to run the uninstaller,
enter `n` or the successfully built package may be erased. Because the installer's
embedded evdi version is replaced with the cloned version already, it should
see the same version and ignore the install request.

### Credits
 - [Displaylink-rpm patch](https://github.com/SimonSchwendele/displaylink-rpm/blob/master/evdiFix660.diff)
 - [evdi issue thread](https://github.com/DisplayLink/evdi/issues/433)
   - [cedricoijakkers's fix](https://github.com/DisplayLink/evdi/issues/433#issuecomment-1812465435)
 - [Displaylink porting documentation](https://support.displaylink.com/knowledgebase/articles/679060)
