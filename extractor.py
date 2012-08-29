#!/usr/bin/env python

import os, sys
import ConfigParser, json, random
import UnRAR2
from UnRAR2.rar_exceptions import *
import zipfile

def get_random_dir(root_dir):
    while True:
        l = []
        for i in range(10):
            l.append(random.choice('abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ1234567890'))
        tmp_dir = ''.join(l)
        if os.access(root_dir + os.path.sep + tmp_dir, os.R_OK) == False:
            return tmp_dir

if len(sys.argv) != 3 or sys.argv[1] != '-f':
    print 'Usage: extractor.exe -f <file>'
    os.exit(1)

file_name = sys.argv[2]

config = ConfigParser.ConfigParser()
try:
    config.readfp(open('config.ini'))
except:
    print 'Make sure the "config.ini" file is under this directory!'
    os.exit(1)

status_update_interval = int(config.get('extractor', 'status_update_interval'))
path_to_extractions_text_file = config.get('extractor', 'path_to_extractions_text_file')
path_to_folder_containg_archives_to_extract = config.get('extractor', 'path_to_folder_containg_archives_to_extract')
path_to_folder_containing_extracted_files = config.get('extractor', 'path_to_folder_containing_extracted_files')
path_to_log_file = config.get('extractor', 'path_to_log_file')
enable_debug_log = config.get('extractor', 'enable_debug_log')

actual_file_path = path_to_folder_containg_archives_to_extract + os.path.sep + file_name

error_string = ''
out_dir = get_random_dir(path_to_folder_containing_extracted_files)
real_out_dir = path_to_folder_containing_extracted_files + os.path.sep + out_dir

if file_name.endswith('.zip'):

    # process .zip file
    try:
        zipfile.ZipFile(actual_file_path).extractall(path=real_out_dir)
    except zipfile.BadZipfile:
        error_string = 'Zip file is broken.'
    except IOError:
        error_string = 'File does not exist.'

elif file_name.endswith('.rar'):

    # process .rar file
    try:
        UnRAR2.RarFile(actual_file_path).extract(path=real_out_dir)
    except ArchiveHeaderBroken:
        error_string = 'The header of archive is broken.'
    except InvalidRARArchive:
        error_string = 'Invalid RAR archive.'
    except FileOpenError:
        error_string = 'Cannot open this file.'
    except IncorrectRARPassword:
        error_string = 'Password needed.'
    except InvalidRARArchiveUsage:
        error_string = 'Invalid RAR archive usage.'
    except:
        error_string = 'Unknown Errors.'

else:
    print 'Unknown file type.'
    print 'Pass .zip or .rar file instead!'
    os.exit(1)

lines = open(path_to_extractions_text_file).readlines()

status = 'finished'
message = out_dir
if error_string != '':
    status = 'error'
    message = error_string
entry = [ '\t{\n',
          '\t\n',
          '\t\t"file":"' + file_name + '",\n',
          '\t\t"status":"' + status + '",\n',
          '\t\t"message":"' + message + '"\n',
          '\t}\n',
          ']\n'
        ]
lines = lines[:-1] + entry

with open(path_to_extractions_text_file, 'w+') as f:
    f.writelines(lines)
