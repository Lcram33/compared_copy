import sys
from colorama import Fore, Style
from os import listdir
from os.path import isdir, isfile, join
from shutil import move
import re


def check_filename_ok_for_ntfs(filename):
    if filename.startswith(' ') or filename.endswith(' ') or filename.endswith('.'):
        return False
    
    disallowed = u"\u0000\\:*?\"<>|"
    for dis in disallowed:
        if dis in filename:
            return False
    
    return True

def normalize_name(filename):
    if filename.startswith(' '):
        filename = filename[re.search(r'[^ ]', filename).start():]

    temp = [x for x in filename.split('.') if x != '']
    filename = '.'.join([''] + temp if filename.startswith('.') else temp)

    while filename.endswith('.') or filename.endswith(' '):
        filename = filename[0:len(filename)-1]

    clean = ""

    disallowed = u"\u0000\\/:*?\"<>|"
    for char in filename:
        if char not in disallowed:
            clean += char
    
    return clean

def rename_file(path):
    temp = path.split('/')
    filename = temp[len(temp)-1]

    temp.remove(filename)
    temp.append(normalize_name(filename))

    new_path = '/'.join(temp)

    move(path, new_path)

def path_scan(path):
    items = listdir(path)

    for item in items:
        temp_path = join(path, item)

        if isdir(temp_path):
            path_scan(temp_path)

        if (isdir(temp_path) or isfile(temp_path)) and not check_filename_ok_for_ntfs(item):
            rename_file(temp_path)
            print(temp_path + " renamed.")


def main():
    args = sys.argv[1:]

    if len(args) != 1:
        print(Fore.RED + "Please provide a path." + Style.RESET_ALL)
        return

    source_path = args[0]

    print("Starting.")
    path_scan(source_path)
    print("Stopping.")

main()