from os.path import getsize, isdir, join, exists, getmtime
from os import listdir, walk, remove
from shutil import rmtree, copy2, copytree
from datetime import datetime
import time


delete_path_list = []
delete_no_longer_exists = ""
delete_size_missmatch = ""
delete_date_missmatch = ""
total_delete_size = 0
delete_files_count = 0
deleted_list = ""
delete_failed = ""
delete_dirs = ""

copy_path_list = []
copy_files = ""
copy_dirs = ""
total_copy_size = 0
total_copy_count = 0
copied_list = ""
copy_failed = ""


def human_readable_modification_date(os_date: float):
    return time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(os_date))

def file_name_time(input_date: datetime):
    return str(input_date).split('.')[0].replace(':', '-').replace(' ', '.')

def rec_dir_file_count(dir_path: str):
    count = len([file for file in listdir(dir_path) if not isdir(join(dir_path, file))])

    for dir in [dir for dir in listdir(dir_path) if isdir(join(dir_path, dir))]:
        count += rec_dir_file_count(join(dir_path, dir))

    return count

def dir_files_size_count(dir_path: str):
    total_size = 0
    for dirpath, dirnames, filenames in walk(dir_path):
        for f in filenames:
            fp = join(dirpath, f)
            total_size += getsize(fp)
    return total_size

def convert_size(size_in_bytes: int):
    units = ['TB', 'GB', 'MB', 'KB']
    size_range = list(range(1,len(units)+1))[::-1]

    for i in size_range:
        converted = size_in_bytes // (10**(3*i))
        if converted > 0:
            return str(converted) + ' ' + units[::-1][i-1]

    return str(size_in_bytes) + ' B'

def scan_delete(source_path: str, destination_path: str, current_sub_path: str):
    global delete_path_list
    global delete_no_longer_exists
    global delete_size_missmatch
    global delete_date_missmatch
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
                delete_size_missmatch += dest_path + f" (src : {convert_size(src_size)}, dest : {convert_size(dest_size)})\n"
                delete_files_count += 1
            else:
                src_date = getmtime(src_path)
                dest_date = getmtime(dest_path)

                if src_date != dest_date:
                    delete_path_list.append(dest_path)
                    total_delete_size += getsize(dest_path)
                    delete_date_missmatch += dest_path + f" (src : {human_readable_modification_date(src_date)}, dest : {human_readable_modification_date(dest_date)})\n"
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

def scan_copy(source_path: str, destination_path: str, current_sub_path: str):
    global copy_path_list
    global delete_path_list
    global total_copy_size
    global total_copy_count
    global copy_files
    global copy_dirs

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
            copy_path_list.append({'src': src_path, 'dest': dest_path})
            total_copy_size += getsize(src_path)
            copy_files += src_path + '\n'
            total_copy_count += 1

    for dir in source_dirs:
        src_dir = join(current_src_path, dir)
        dest_dir = join(current_dest_path, dir)

        if dir not in destination_dirs or dest_dir in delete_path_list:
            copy_path_list.append({'src': src_dir, 'dest': dest_dir})
            dir_size = dir_files_size_count(src_dir)
            dir_count = rec_dir_file_count(src_dir)
            copy_dirs += src_dir + f" ({dir_count} files, {convert_size(dir_size)})\n"
            total_copy_count += dir_count
            total_copy_size += dir_size
        else:
            if len(listdir(src_dir)) > 0:
                scan_copy(source_path, destination_path, src_dir.replace(source_path, ''))


def delete():
    global delete_path_list
    global deleted_list
    global delete_failed

    if len(delete_path_list) == 0:
        print("Rien à supprimer !")
        return

    for delete_path in delete_path_list:
        try:
            if isdir(delete_path):
                rmtree(delete_path)
            else:
                remove(delete_path)
            deleted_list += delete_path + '\n'
        except Exception as e:
            delete_failed += delete_path + ", error : " + str(e) + '\n'

def copy():
    global copy_path_list
    global copied_list
    global copy_failed

    for copy_path in copy_path_list:
        try:
            if isdir(copy_path['src']):
                copytree(copy_path['src'], copy_path['dest'])
            else:
                copy2(copy_path['src'], copy_path['dest'])
            copied_list += copy_path['src'] + '\n'
        except Exception as e:
            copy_failed += copy_path['src'] + ", error : " + str(e) + '\n'


def main():
    global delete_no_longer_exists
    global delete_size_missmatch
    global delete_date_missmatch
    global delete_dirs
    global total_delete_size
    global delete_files_count
    global deleted_list
    global copied_list
    global copy_failed
    global delete_failed

    splash = """
░█████╗░░█████╗░███╗░░░███╗██████╗░░█████╗░██████╗░███████╗██████╗░  ░█████╗░░█████╗░██████╗░██╗░░░██╗
██╔══██╗██╔══██╗████╗░████║██╔══██╗██╔══██╗██╔══██╗██╔════╝██╔══██╗  ██╔══██╗██╔══██╗██╔══██╗╚██╗░██╔╝
██║░░╚═╝██║░░██║██╔████╔██║██████╔╝███████║██████╔╝█████╗░░██║░░██║  ██║░░╚═╝██║░░██║██████╔╝░╚████╔╝░
██║░░██╗██║░░██║██║╚██╔╝██║██╔═══╝░██╔══██║██╔══██╗██╔══╝░░██║░░██║  ██║░░██╗██║░░██║██╔═══╝░░░╚██╔╝░░
╚█████╔╝╚█████╔╝██║░╚═╝░██║██║░░░░░██║░░██║██║░░██║███████╗██████╔╝  ╚█████╔╝╚█████╔╝██║░░░░░░░░██║░░░
░╚════╝░░╚════╝░╚═╝░░░░░╚═╝╚═╝░░░░░╚═╝░░╚═╝╚═╝░░╚═╝╚══════╝╚═════╝░  ░╚════╝░░╚════╝░╚═╝░░░░░░░░╚═╝░░░
    """

    print(splash)

    source_path = input("Source path (files will be copied FROM this folder) : ")
    destination_path = input("Destination path (files will be copied IN this folder) : ")

    if not exists(source_path) or not isdir(source_path):
        print("The source path is not valid (does not exists or is not a folder).")
        return

    if not exists(destination_path) or not isdir(destination_path):
        print("The destination path is not valid (does not exists or is not a folder).")
        return

    print()
    print()
    print("INITIAL SCAN")
    print("WARNING : beyond this point, any change made in the source or destination folder WILL NOT be taken into account.")
    print("This WILL NOT affect your files. It will generate a report of exactly what will be done in the next step.")

    check = input("Perform initial scan ? (y/n) ")
    print()
    print()
    if check == 'y':
        print("Scan in progress, please wait, this can take a while.")

        scan_delete(source_path, destination_path, '')
        scan_copy(source_path, destination_path, '')

        gen_date = datetime.now()
        filename = f"scan.{file_name_time(gen_date)}.log"
        f = open(filename, 'w')
        f.write(splash + '\n' + f"""
Report generated on {str(gen_date)}



DELETE
Delete {delete_files_count} files, {convert_size(total_delete_size) + " (or " + str(total_delete_size) + " B)" if total_delete_size >= 1000 else convert_size(total_delete_size)} of data.

DETAILS
No longer exists on source
{delete_no_longer_exists}

No longer exists on source (folders)
{delete_dirs}

Size does not match
{delete_size_missmatch}

Last modification date does not match
{delete_date_missmatch}



COPY
Copy {total_copy_count} files, {convert_size(total_copy_size) + " (or " + str(total_copy_size) + " B)" if total_copy_size >= 1000 else convert_size(total_copy_size)} of data.

DETAILS
Files :
{copy_files}

Folders :
{copy_dirs}
        """)
        f.close()

        print(f"Scan complete ! See the results in {filename}.")

    else:
        return

    print()
    print()
    print("PROCEED")
    print("WARNING : this will be done according to the previous scan. Any change made in the source or destination folder after the scan WILL NOT be taken into account.")
    print("WARNING : This WILL affect your files. Make sure to read the report !")

    check = input("Perform compared copy ? (y/n) ")
    print()
    print()
    if check == 'y':
        print("PROCEEDING. Please wait and do not close this window. This can take a while.")

        delete()
        copy()

        gen_date = datetime.now()
        filename = f"report.{file_name_time(gen_date)}.log"
        f = open(filename, 'w')
        f.write(splash + '\n' + f"""
Report generated on {str(gen_date)}

DELETED
{deleted_list}

DELTE FAILED
{delete_failed if len(delete_failed) > 0 else "None !"}

COPIED
{copied_list}

COPY FAILED
{copy_failed if len(copy_failed) > 0 else "None !"}
        """)
        f.close()

        print(f"Done ! See the results in {filename}.")
    else:
        return

    return

main()
