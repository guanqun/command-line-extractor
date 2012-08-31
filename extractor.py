#!/usr/bin/env python

import os, sys
import ConfigParser, json, random, collections
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
    sys.exit(1)

file_name = sys.argv[2]

config = ConfigParser.ConfigParser()
try:
    config.readfp(open('config.ini'))
except:
    print 'Make sure the "config.ini" file is under this directory!'
    sys.exit(1)

status_update_interval = int(config.get('extractor', 'status_update_interval'))
path_to_extractions_text_file = config.get('extractor', 'path_to_extractions_text_file')
path_to_folder_containg_archives_to_extract = config.get('extractor', 'path_to_folder_containg_archives_to_extract')
path_to_folder_containing_extracted_files = config.get('extractor', 'path_to_folder_containing_extracted_files')
path_to_log_file = config.get('extractor', 'path_to_log_file')
enable_debug_log = config.get('extractor', 'enable_debug_log')

# output debug log after we passed config.ini
if enable_debug_log == 'true':
    with open(path_to_log_file, 'a+') as f:
        f.write('config.ini parsed result:\n')
        f.write('\tstatus update interval: %d' % (status_update_interval,) + '\n')
        f.write('\tpath to extractions text file: ' + path_to_extractions_text_file + '\n')
        f.write('\tpath to folder containing archives to extract: ' + path_to_folder_containg_archives_to_extract + '\n')
        f.write('\tpath to folder containing extracted files: ' + path_to_folder_containing_extracted_files + '\n')
        f.write('\tpath to log file: ' + path_to_log_file + '\n')
        f.write('\tenable debug log: ' + enable_debug_log + '\n')

actual_file_path = path_to_folder_containg_archives_to_extract + os.path.sep + file_name

error_string = ''
out_dir = get_random_dir(path_to_folder_containing_extracted_files)
real_out_dir = path_to_folder_containing_extracted_files + os.path.sep + out_dir

# output debug log when starting to extract
if enable_debug_log == 'true':
    with open(path_to_log_file, 'a+') as f:
        f.write('start to extract ' + actual_file_path + ' ... ')

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
    error_string = 'Unknown file type.'

# output entry's status and message
status = 'finished'
message = out_dir
if error_string != '':
    status = 'error'
    message = error_string

# output debug log when it's done
if enable_debug_log == 'true':
    with open(path_to_log_file, 'a+') as f:
        if error_string != '':
            f.write('failed (' + message + ')\n')
        else:
            f.write('succeed!\n')

entries = []

try:
    f = open(path_to_extractions_text_file)
    entries = json.load(f, object_pairs_hook=collections.OrderedDict)
    f.close()

    entries = [item for item in entries if item['file'] != file_name]
except:
    pass

this_entry = collections.OrderedDict([('file', file_name), ('status', status), ('message', message)])
entries.append(this_entry)
with open(path_to_extractions_text_file, 'w+') as f:
    f.write(json.dumps(entries, sort_keys=False, indent=4))
