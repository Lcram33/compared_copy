from os.path import getsize, isdir, join, exists, getmtime
from os import listdir, walk, remove, get_terminal_size, getcwd, getlogin
from shutil import rmtree, copy2, copytree
from colorama import Fore, Style
from datetime import datetime
import time
import hashlib
import sys
import re
import threading


if exists('./ignore_dirs.list'):
    with open('ignore_dirs.list', 'r') as f:
        ignore_dirs = [x.replace('\n','') for x in f.readlines() if x != '\n']
else:
    ignore_dirs = []

if exists('./ignore_files.list'):
    with open('ignore_files.list', 'r') as f:
        ignore_files = [x.replace('\n','') for x in f.readlines() if x != '\n']
else:
    ignore_files = []

if exists('./md5.list'):
    with open('md5.list', 'r') as f:
        md5_files_check = [x.replace('\n','') for x in f.readlines() if x != '\n']
else:
    md5_files_check = []


delete_path_list = []
delete_no_longer_exists = ""
delete_size_missmatch = ""
delete_date_missmatch = ""
delete_md5_missmatch = ""
total_delete_size = 0
delete_files_count = 0

deleted_list = ""
delete_failed = ""
delete_dirs = ""
deleted_count = 0
delete_failed_count = 0

copy_path_list = []
copy_files = ""
copy_dirs = ""
copy_ignored_files = ""
copy_ignored_dirs = ""
total_copy_size = 0
total_copy_count = 0

copied_list = ""
copy_failed = ""
copied_count = 0
copy_failed_count = 0

total_op = 0
current_op_count = 0
op_percent = 0


def animated_loading():
    chars = ["⢿", "⣻", "⣽", "⣾", "⣷", "⣯", "⣟", "⡿"]
    for char in chars:
        sys.stdout.write('\r'+'Scanning ' + char + '\t')
        time.sleep(.1)
        sys.stdout.flush() 

def animated_percent_bar(percent):
    filled_squares = round(percent/10)
    bar = '[' + filled_squares * '■' + (10 - filled_squares) * '□' + f"] {percent}%\t"
    sys.stdout.flush()
    sys.stdout.write('\r'+bar)

def insert_plus(path):
    return Fore.GREEN + '[+] ' + Style.RESET_ALL + path + '\n'

def insert_minus(path):
    return Fore.RED + '[-] ' + Style.RESET_ALL + path + '\n'

def insert_ignored(path):
    return Fore.YELLOW + '[x] ' + Style.RESET_ALL + path + '\n'

def add_colors(str_data, type):
    new_data = ""
    if type == '+':
        for line in str_data.split('\n'):
            new_data += insert_plus(line) if line != '' else ''
    elif type == '-':
        for line in str_data.split('\n'):
            new_data += insert_minus(line) if line != '' else ''
    if type == 'x':
        for line in str_data.split('\n'):
            new_data += insert_ignored(line) if line != '' else ''
        
    return new_data

def print_separator():
    print(Fore.BLUE + '-' * get_terminal_size().columns + Style.RESET_ALL)

def md5(path):
    hash_md5 = hashlib.md5()
    with open(path, "rb") as f:
        for chunk in iter(lambda: f.read(4096), b""):
            hash_md5.update(chunk)
    return hash_md5.hexdigest()

def human_readable_modification_date(os_date):
    return time.strftime('%d/%m/%Y %H:%M:%S', time.localtime(os_date))

def check_date_delta(src_date, dest_date, delta):
    #It looks like some files that have not been edited have a different modification date, which does not exceed 2 seconds, so this is mitigated using the following check.
    return abs(round(src_date)-round(dest_date)) >= delta

def file_name_time(input_date):
    return str(input_date).split('.')[0].replace(':', '-').replace(' ', '.').replace('/', '-')

def rec_dir_file_count(dir_path):
    count = len([file for file in listdir(dir_path) if not isdir(join(dir_path, file))])

    for dir in [dir for dir in listdir(dir_path) if isdir(join(dir_path, dir))]:
        count += rec_dir_file_count(join(dir_path, dir))

    return count

def dir_files_size_count(dir_path):
    total_size = 0
    for dirpath, dirnames, filenames in walk(dir_path):
        for f in filenames:
            fp = join(dirpath, f)
            total_size += getsize(fp)
    
    return total_size

def convert_size(size_in_bytes):
    units = ['TB', 'GB', 'MB', 'KB']
    size_range = list(range(1,len(units)+1))[::-1]

    for i in size_range:
        converted = size_in_bytes // (10**(3*i))
        if converted > 0:
            return str(converted) + ' ' + units[::-1][i-1]

    return str(size_in_bytes) + ' B'

def ignore_dir(dir_name):
    return any(re.search(x, dir_name) for x in ignore_dirs)

def ignore_file(file_name):
    return any(re.search(x, file_name) for x in ignore_files)

def has_to_check_md5(file_name):
    return any(re.search(x, file_name) for x in md5_files_check)


def scan_delete(source_path, destination_path, current_sub_path):
    global delete_path_list
    global delete_no_longer_exists
    global delete_size_missmatch
    global delete_date_missmatch
    global delete_md5_missmatch
    global delete_dirs
    global total_delete_size
    global delete_files_count

    if len(current_sub_path) > 0 and current_sub_path[0] == '/':
        current_sub_path = current_sub_path[1:]

    destination_files = [file for file in listdir(join(destination_path, current_sub_path)) if not isdir(join(destination_path, current_sub_path, file))]
    destination_dirs = [file for file in listdir(join(destination_path, current_sub_path)) if isdir(join(join(destination_path, current_sub_path), file))]
    source_files = [file for file in listdir(join(source_path, current_sub_path)) if not isdir(join(join(source_path, current_sub_path), file))]
    source_dirs = [file for file in listdir(join(source_path, current_sub_path)) if isdir(join(join(source_path, current_sub_path), file))]

    temp_path = join(destination_path, current_sub_path)

    for file in destination_files:
        dest_path = join(temp_path, file)

        if file not in source_files:
            delete_path_list.append(dest_path)
            total_delete_size += getsize(dest_path)
            delete_no_longer_exists += dest_path + '\n'
            delete_files_count += 1
        else:
            src_path = join(source_path, current_sub_path, file)

            src_size = getsize(src_path)
            dest_size = getsize(dest_path)

            if src_size != dest_size:
                delete_path_list.append(dest_path)
                total_delete_size += getsize(dest_path)
                delete_size_missmatch += dest_path + f" (src : {convert_size(src_size)} or {src_size} B, dest : {convert_size(dest_size)} or {dest_size} B)\n"
                delete_files_count += 1
            else:
                if has_to_check_md5(file):
                    src_md5sum = md5(src_path)
                    dest_md5sum = md5(dest_path)

                    if src_md5sum != dest_md5sum:
                        delete_path_list.append(dest_path)
                        total_delete_size += getsize(dest_path)
                        delete_md5_missmatch += dest_path + f" (src : {src_md5sum}, dest : {dest_md5sum})\n"
                        delete_files_count += 1
                else:
                    #src_date = getmtime(src_path)
                    #dest_date = getmtime(dest_path)
                    src_date = human_readable_modification_date(getmtime(src_path))
                    dest_date = human_readable_modification_date(getmtime(dest_path))

                    if src_date != dest_date: #and check_date_delta(src_date, dest_date, 3):
                        delete_path_list.append(dest_path)
                        total_delete_size += getsize(dest_path)
                        #delete_date_missmatch += dest_path + f" (src : {human_readable_modification_date(src_date)}, dest : {human_readable_modification_date(dest_date)})\n"
                        delete_date_missmatch += dest_path + f" (src : {src_date}, dest : {dest_date})\n"
                        delete_files_count += 1

    for dir in destination_dirs:
        dir_path = join(temp_path, dir)
        if dir not in source_dirs:
            delete_path_list.append(dir_path)
            dir_size = dir_files_size_count(dir_path)
            dir_count = rec_dir_file_count(dir_path)
            delete_dirs += dir_path + f" ({dir_count} files, {convert_size(dir_size)})\n"
            delete_files_count += dir_count
            total_delete_size += dir_size
        else:
            if len(listdir(dir_path)) > 0:
                scan_delete(source_path, destination_path, dir_path.replace(destination_path, ''))

def scan_copy(source_path, destination_path, current_sub_path):
    global copy_path_list
    global delete_path_list
    global total_copy_size
    global total_copy_count
    global copy_files
    global copy_dirs
    global copy_ignored_files
    global copy_ignored_dirs

    if len(current_sub_path) > 0 and current_sub_path[0] == '/':
        current_sub_path = current_sub_path[1:]

    destination_files = [file for file in listdir(join(destination_path, current_sub_path)) if not isdir(join(destination_path, current_sub_path, file))]
    destination_dirs = [file for file in listdir(join(destination_path, current_sub_path)) if isdir(join(join(destination_path, current_sub_path), file))]
    source_files = [file for file in listdir(join(source_path, current_sub_path)) if not isdir(join(join(source_path, current_sub_path), file))]
    source_dirs = [file for file in listdir(join(source_path, current_sub_path)) if isdir(join(join(source_path, current_sub_path), file))]

    current_dest_path = join(destination_path, current_sub_path)
    current_src_path = join(source_path, current_sub_path)

    for file in source_files:
        src_path = join(current_src_path, file)
        dest_path = join(current_dest_path, file)

        if file not in destination_files or dest_path in delete_path_list:
            if ignore_file(file):
                copy_ignored_files += src_path + '\n'
            else:
                copy_path_list.append({'src': src_path, 'dest': dest_path})
                total_copy_size += getsize(src_path)
                copy_files += src_path + '\n'
                total_copy_count += 1

    for dir in source_dirs:
        src_dir = join(current_src_path, dir)
        dest_dir = join(current_dest_path, dir)

        if dir not in destination_dirs or dest_dir in delete_path_list:
            if ignore_dir(dir):
                copy_ignored_dirs += src_dir + '\n'
            else:
                copy_path_list.append({'src': src_dir, 'dest': dest_dir})
                dir_size = dir_files_size_count(src_dir)
                dir_count = rec_dir_file_count(src_dir)
                copy_dirs += src_dir + f" ({dir_count} files, {convert_size(dir_size)})\n"
                total_copy_count += dir_count
                total_copy_size += dir_size
        else:
            if len(listdir(src_dir)) > 0:
                if ignore_dir(dir):
                    copy_ignored_dirs += src_dir + '\n'
                else:
                    scan_copy(source_path, destination_path, src_dir.replace(source_path, ''))


def delete():
    global deleted_list
    global delete_failed
    global deleted_count
    global delete_failed_count
    global op_percent
    global total_op
    global current_op_count

    total_op = len(delete_path_list) + len(copy_path_list)

    for delete_path in delete_path_list:
        try:
            if isdir(delete_path):
                temp = rec_dir_file_count(delete_path)
                rmtree(delete_path)
                deleted_count += temp
            else:
                remove(delete_path)
                deleted_count += 1
            deleted_list += delete_path + (' (dir)' if isdir(delete_path) else '') + '\n'
        except Exception as e:
            delete_failed += delete_path + ", error : " + str(e) + '\n'
            delete_failed_count += 1
        
        current_op_count += 1
        op_percent = round(100 * current_op_count / total_op)

def copy():
    global copied_list
    global copy_failed
    global copied_count
    global copy_failed_count
    global op_percent
    global total_op
    global current_op_count

    for copy_path in copy_path_list:
        try:
            if isdir(copy_path['src']):
                temp = rec_dir_file_count(copy_path['src'])
                copytree(copy_path['src'], copy_path['dest'])
                copied_count += temp
            else:
                copy2(copy_path['src'], copy_path['dest'])
                copied_count += 1
            copied_list += copy_path['src'] + '\n'
        except Exception as e:
            copy_failed += copy_path['src'] + ", error : " + str(e) + '\n'
            copy_failed_count += 1
        
        current_op_count += 1
        op_percent = round(100 * current_op_count / total_op)
    
    time.sleep(.5)


def main_noargs():
    splash = """
░█████╗░░█████╗░███╗░░░███╗██████╗░░█████╗░██████╗░███████╗██████╗░  ░█████╗░░█████╗░██████╗░██╗░░░██╗
██╔══██╗██╔══██╗████╗░████║██╔══██╗██╔══██╗██╔══██╗██╔════╝██╔══██╗  ██╔══██╗██╔══██╗██╔══██╗╚██╗░██╔╝
██║░░╚═╝██║░░██║██╔████╔██║██████╔╝███████║██████╔╝█████╗░░██║░░██║  ██║░░╚═╝██║░░██║██████╔╝░╚████╔╝░
██║░░██╗██║░░██║██║╚██╔╝██║██╔═══╝░██╔══██║██╔══██╗██╔══╝░░██║░░██║  ██║░░██╗██║░░██║██╔═══╝░░░╚██╔╝░░
╚█████╔╝╚█████╔╝██║░╚═╝░██║██║░░░░░██║░░██║██║░░██║███████╗██████╔╝  ╚█████╔╝╚█████╔╝██║░░░░░░░░██║░░░
░╚════╝░░╚════╝░╚═╝░░░░░╚═╝╚═╝░░░░░╚═╝░░╚═╝╚═╝░░╚═╝╚══════╝╚═════╝░  ░╚════╝░░╚════╝░╚═╝░░░░░░░░╚═╝░░░
    """

    print_separator()
    print(Fore.LIGHTCYAN_EX + splash + Style.RESET_ALL)
    print_separator()
    print()

    source_path = input("Source path (files will be copied FROM this folder) : ")
    destination_path = input("Destination path (files will be copied IN this folder) : ")

    if source_path.startswith('.'):
        print("Using current path as source starts with .")
        source_path = getcwd() + source_path[1:len(source_path)]
    
    if destination_path.startswith('.'):
        print("Using current path as destination starts with .")
        destination_path = getcwd() + destination_path[1:len(destination_path)]
    
    if source_path.startswith('~'):
        print("Using home path as source starts with ~")
        source_path = f"/home/{getlogin()}/{source_path[1:len(source_path)]}"
    
    if destination_path.startswith('.'):
        print("Using home path as destination starts with ~")
        destination_path = f"/home/{getlogin()}/{destination_path[1:len(destination_path)]}"

    if not exists(source_path) or not isdir(source_path):
        print(Fore.RED + "The source path is not valid (does not exists or is not a folder)." + Style.RESET_ALL)
        return

    if not exists(destination_path) or not isdir(destination_path):
        print(Fore.RED + "The destination path is not valid (does not exists or is not a folder)." + Style.RESET_ALL)
        return

    print()
    print()
    print_separator()
    print("INITIAL SCAN")
    print(Fore.YELLOW + "WARNING : beyond this point, any change made in the source or destination folder WILL NOT be taken into account." + Style.RESET_ALL)
    print("This WILL NOT affect your files. It will generate a report of exactly what will be done in the next step.")

    check = input("Perform initial scan ? (y/n) ")
    print()
    print()
    if check == 'y':
        print_separator()
        print("Scan in progress, please wait, this can take a while.")

        start = time.time()

        the_process = threading.Thread(name='process', target=scan_delete, args=(source_path, destination_path, '',))
        the_process.start()
        while the_process.is_alive():
            animated_loading()

        the_process = threading.Thread(name='process', target=scan_copy, args=(source_path, destination_path, '',))
        the_process.start()
        while the_process.is_alive():
            animated_loading()

        end = time.time()

        delay = round(end - start)

        md5res = f"""
md5sum does not match
{delete_md5_missmatch}
        """ if len(delete_md5_missmatch) > 0 else '\n'

        gen_date = datetime.now()
        filename = f"scan.{file_name_time(gen_date)}.log"
        f = open(filename, 'w')
        f.write(splash + '\n' + f"""
Report generated on {str(gen_date)}

Source : {source_path}
Destination : {destination_path}



DELETE
Delete {delete_files_count} files, {convert_size(total_delete_size) + " (or " + str(total_delete_size) + " B)" if total_delete_size >= 1000 else convert_size(total_delete_size)} of data.

COPY
Copy {total_copy_count} files, {convert_size(total_copy_size) + " (or " + str(total_copy_size) + " B)" if total_copy_size >= 1000 else convert_size(total_copy_size)} of data.

Done in {delay} s.



DELETE DETAILS

No longer exists on source
{delete_no_longer_exists}

No longer exists on source (folders)
{delete_dirs}

Size does not match
{delete_size_missmatch}

Last modification date does not match
{delete_date_missmatch}
{md5res}

COPY DETAILS

Files :
{copy_files}

Folders :
{copy_dirs}

Ignored files :
{copy_ignored_files}

Ignored dirs :
{copy_ignored_dirs}
        """)
        f.close()

        print(f"Scan complete ! See the results in {filename}.")
        print(f"""
SUMMARY
Delete {delete_files_count} files, {convert_size(total_delete_size) + " (or " + str(total_delete_size) + " B)" if total_delete_size >= 1000 else convert_size(total_delete_size)} of data.
Copy {total_copy_count} files, {convert_size(total_copy_size) + " (or " + str(total_copy_size) + " B)" if total_copy_size >= 1000 else convert_size(total_copy_size)} of data.

Done in {delay} s.
        """)

    else:
        return

    print()
    print()

    if len(delete_path_list) == 0 and len(copy_path_list) == 0:
        print("Nothing to do !")
        return

    print_separator()
    print("PROCEED")
    print(Fore.YELLOW + "WARNING : this will be done according to the previous scan. Any change made in the source or destination folder after the scan WILL NOT be taken into account." + Style.RESET_ALL)
    print(Fore.YELLOW + "WARNING : This WILL affect your files. Make sure to read the report !" + Style.RESET_ALL)

    check = input("Perform compared copy ? (y/n) ")
    print()
    print()
    if check == 'y':
        print("PROCEEDING. Please wait and do not close this window. This can take a while.")

        start = time.time()

        the_process = threading.Thread(name='process', target=delete)
        the_process.start()
        while the_process.is_alive():
            animated_percent_bar(op_percent)

        the_process = threading.Thread(name='process', target=copy)
        the_process.start()
        while the_process.is_alive():
            animated_percent_bar(op_percent)

        end = time.time()

        percent_deleted = None if delete_files_count == 0 else round(100 * deleted_count / delete_files_count)
        percent_copied = None if total_copy_count == 0 else round(100 * copied_count / total_copy_count)

        delay = round(end - start)

        gen_date = datetime.now()
        filename = f"report.{file_name_time(gen_date)}.log"
        f = open(filename, 'w')
        f.write(splash + '\n' + f"""
Report generated on {str(gen_date)}

DELETE :    {percent_deleted}% of the scheduled files deleted.
COPY :      {percent_copied}% of the scheduled files copied.

Done in {delay} s.



DELETED : {deleted_count} files

{deleted_list}



DELETE FAILED : {delete_failed_count} failed

{delete_failed if len(delete_failed) > 0 else "None !"}



COPIED : {copied_count} files

{copied_list}



COPY FAILED : {delete_failed_count} failed

{copy_failed if len(copy_failed) > 0 else "None !"}
        """)
        f.close()

        print("Done !")
        print(f"""
SUMMARY
Deleted {deleted_count} files ({percent_deleted}%)
Copied {copied_count} files ({percent_copied}%)

Done in {delay} s.
        """)
        print(f"See more details in {filename}.")
    else:
        print("Canceled, nothing done.")
    
    print_separator()
    

def main():
    args = sys.argv[1:]

    if len(args) == 0:
        main_noargs()
        return

    if len(args) not in [2, 3]:
        print(Fore.RED + "Too few or too much parameters." + Style.RESET_ALL)
        return

    source_path = args[0]
    destination_path = args[1]

    if len(args) == 3:
        try:
            do_confirm = int(args[2])
        except Exception:
            print(Fore.RED + "Invalid third parameter." + Style.RESET_ALL)
            return
        
        if do_confirm not in [0, 1]:
            print(Fore.RED + "Invalid third parameter." + Style.RESET_ALL)
            return
    else:
        do_confirm = 0
    
    if do_confirm:
        print(Fore.YELLOW + "AUTOCONFIRM ENABLED - Will copy directly after scan." + Style.RESET_ALL)

    if source_path.startswith('.'):
        print("Using current path as source starts with .")
        source_path = getcwd() + source_path[1:len(source_path)]
    
    if destination_path.startswith('.'):
        print("Using current path as destination starts with .")
        destination_path = getcwd() + destination_path[1:len(destination_path)]

    if not exists(source_path) or not isdir(source_path):
        print(Fore.RED + "The source path is not valid (does not exists or is not a folder)." + Style.RESET_ALL)
        return

    if not exists(destination_path) or not isdir(destination_path):
        print(Fore.RED + "The destination path is not valid (does not exists or is not a folder)." + Style.RESET_ALL)
        return

    print(f"""
Source : {source_path}
Destination : {destination_path}
    """)
    print("COMPARED COPY : scan in progress, please wait, this can take a while.")

    the_process = threading.Thread(name='process', target=scan_delete, args=(source_path, destination_path, '',))
    the_process.start()
    while the_process.is_alive():
        animated_loading()

    the_process = threading.Thread(name='process', target=scan_copy, args=(source_path, destination_path, '',))
    the_process.start()
    while the_process.is_alive():
        animated_loading()
    
    print_separator()

    if len(delete_path_list) == 0 and len(copy_path_list) == 0:
        print("Nothing to do !")
        print_separator()
        return

    md5res = f"""
md5sum does not match
{add_colors(delete_md5_missmatch, '-')}
    """ if len(delete_md5_missmatch) > 0 else '\n'

    print(f"""
RESULT

DELETE
Delete {delete_files_count} files, {convert_size(total_delete_size) + " (or " + str(total_delete_size) + " B)" if total_delete_size >= 1000 else convert_size(total_delete_size)} of data.

COPY
Copy {total_copy_count} files, {convert_size(total_copy_size) + " (or " + str(total_copy_size) + " B)" if total_copy_size >= 1000 else convert_size(total_copy_size)} of data.

DELETE DETAILS

No longer exists on source
{add_colors(delete_no_longer_exists, '-')}

No longer exists on source (folders)
{add_colors(delete_dirs, '-')}

Size does not match
{add_colors(delete_size_missmatch, '-')}

Last modification date does not match
{add_colors(delete_date_missmatch, '-')}
{md5res}
COPY DETAILS

Files :
{add_colors(copy_files, '+')}

Folders :
{add_colors(copy_dirs, '+')}

Ignored files :
{add_colors(copy_ignored_files, 'x')}

Ignored dirs :
{add_colors(copy_ignored_dirs, 'x')}
    """)
    print_separator()

    if not do_confirm:
        print("PROCEED")
        check = input(Fore.YELLOW + "Perform compared copy ? (y/n) " + Style.RESET_ALL)
        if check == 'y':
            print("PROCEEDING. Please wait and do not close this window. This can take a while.")

            the_process = threading.Thread(name='process', target=delete)
            the_process.start()
            while the_process.is_alive():
                animated_percent_bar(op_percent)
            
            the_process = threading.Thread(name='process', target=copy)
            the_process.start()
            while the_process.is_alive():
                animated_percent_bar(op_percent)
            
        else:
            print("Canceled, nothing done.")
            return
    else:
        print("PROCEEDING. Please wait and do not close this window. This can take a while.")

        the_process = threading.Thread(name='process', target=delete)
        the_process.start()
        while the_process.is_alive():
            animated_percent_bar(op_percent)
        
        the_process = threading.Thread(name='process', target=copy)
        the_process.start()
        while the_process.is_alive():
            animated_percent_bar(op_percent)

    percent_deleted = None if delete_files_count == 0 else round(100 * deleted_count / delete_files_count)
    percent_copied = None if total_copy_count == 0 else round(100 * copied_count / total_copy_count)
    
    print(f"""
DONE

DELETE :    {percent_deleted}% of the scheduled files deleted.
COPY :      {percent_copied}% of the scheduled files copied.
    """)

    print_separator()


main()