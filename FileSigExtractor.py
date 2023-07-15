__author__ = "Abhiram Kumar (stuxnet999)"

import magic
import os
import csv
import argparse

argParser = argparse.ArgumentParser(
    description='''FileSigExtractor - Python based tool to extract signatures of all files within a directory''')

argParser.add_argument("-d","--directory", help="Specify directory path")
argParser.add_argument("-o","--output-dir", help="Specify CSV output directory path")

args = argParser.parse_args()
directory = args.directory
output = args.output_dir


if not os.path.isdir(args.output_dir):
    os.makedirs(args.output_dir)

print("FileSigExtractor - Python based tool to extract signatures of all files within a directory\n")
print("GitHub - https://github.com/stuxnet999/FileSigExtractor\n")
print("===========================================================\n")

unknown_files = os.path.join(output,"Unknown-Files.csv")
known_files = os.path.join(output,"Matched-Files.csv")
error_files = os.path.join(output, "Errors-Encountered.txt")
large_files = os.path.join(output, "Large-Files-Ignored.txt")
empty_files = os.path.join(output, "Empty-Files.txt")

f = open(unknown_files, "w", newline='')
errors = open(error_files,"w")

file_list = []
large_files_list = []
empty_files_list = []

for root, dirs, files in os.walk(directory):
    for file in files:
        file_path = os.path.join(root, file)

        try:
            size = os.stat(file_path).st_size

            if (os.stat(file_path).st_size == 0):
                empty_files_list.append(file_path)
            elif (os.stat(file_path).st_size/(1024*1024) >= 512):
                large_files_list.append(file_path)
            else:
                file_list.append(file_path)
        except OSError:
            errors.write("Encountered OSError. Skipping...\n")

if len(large_files_list) > 0:
    print("{} Large files found. Will be ignored. Written to {}".format(len(large_files_list), large_files))
    large_file_writer = open(large_files, "w")
    large_file_writer.write('\n'.join(large_files_list))
    large_file_writer.close()

if len(empty_files) > 0:
    print("{} Empty files found. Will be ignored. Written to {}\n".format(len(empty_files_list), empty_files))
    empty_file_writer = open(empty_files, "w")
    empty_file_writer.write('\n'.join(empty_files_list))
    empty_file_writer.close()

unknown_file_writer = csv.writer(f, dialect='excel')
unknown_file_writer.writerow(["File Path", "Original Extension", "File Type"])

with open(known_files,"w", newline='') as file:
    writer = csv.writer(file, dialect='excel')
    writer.writerow(["File Path", "Original Extension", "File Type"])
    for files in file_list:
        try:
            a = []
            a.append(files)
            a.append(os.path.splitext(files)[1])
            a.append(magic.from_buffer(open(files,"rb").read(2048)))

            if a[2] == "data":
                unknown_file_writer.writerow(a)
            else:
                writer.writerow(a)
            
        except PermissionError:
            errors.write("Encountered PermissionError for {}. Cannot open. Skipping...\n".format(files))
        except FileNotFoundError:
            errors.write("Encountered FileNotFoundError for {}. Cannot open. Skipping...\n".format(files))
        except OSError:
            errors.write("Encountered OSError for {} Cannot open. Skipping...\n".format(files))
    
print("Scanned {} files within {}\n".format(len(file_list), directory))
print("Output for known signatures written to {}".format(known_files))
print("Output for unknown signatures written to {}".format(unknown_files))

f.close()
errors.close()