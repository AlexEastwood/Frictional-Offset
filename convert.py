import xlrd
import csv
import os
import sys

path = sys.path[0]
list_of_files = []
for root, dirs, files in os.walk(path):
    for file in files:
        if file.endswith(".xls"):
            list_of_files.append(os.path.join(root, file))

for file in list_of_files:
    with xlrd.open_workbook(file) as wb:
        sh = wb.sheet_by_index(0)  # or wb.sheet_by_name('name_of_the_sheet_here')
        with open('a_file.csv', 'wb') as f:   # open('a_file.csv', 'w', newline="") for python 3
            c = csv.writer(f)
            for r in range(sh.nrows):
                c.writerow(sh.row_values(r))

