# compared_copy
A light program to copy exactly the content of a folder into another one.
It takes into account the existing files, compares and delete the older versions.

Usage :
python3 compared-copy.py /src/path /dest/path
python3 compared-copy.py

The program works by first creating a full report of what will be done, so you can check which file will be deleted/copied and why.
It apply what is stated in the file, so any change commited after or during the scan will not be considered.

This program works in Linux based systems (worked with two 5TB HDD on fedora and debian).
It seems like it would not work on Windows. Any fix or change is welcomed !

To ignore files or dirs, add names or regex on ignore_dirs.list and ignore_files.list (an example is provided for dirs).

If you want to perform md5sum check rather than last modification date (useful on VeraCrypt containers !), just add the files names or regex on md5.list.

Should you have any question, suggestion, problem, feel free to contact me to lcram33@pm.me or open an issue.