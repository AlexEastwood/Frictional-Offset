import os
import re
import sys
import statistics
import pandas as pd

#Set path to the current directory of the python script
#Find all files in current and child directories of the chosen extension
def find_files_of_type(type):
    path = sys.path[0]
    list_of_files = []
    for root, dirs, files in os.walk(path):
        for file in files:
            if file.endswith("." + type):
                list_of_files.append(os.path.join(root, file))
    return list_of_files

def find_test_ids(list_of_files):
    ids = []
    for file in list_of_files: 
        m = re.match(r"(.*)(_P\d+_\w?)(.*)", file)
        if m.group(2) not in ids:
            ids.append(m.group(2))
    return ids

def find_cycle(file, i):
    columns = pd.read_table(file, skiprows=i)
    df = pd.DataFrame(columns)
    cycle = int(''.join(c for c in str(df.columns)
                        .split(",")[1] if c.isdigit()))
    return cycle

def find_frictional_offset(list_of_files, id):

    #Create arrays to store average coeffs in each file going forward or reverse
    forward = []
    reverse = []

    for file in list_of_files:
        if id not in file:
            continue
        #Ignore the test file
        if "forward" not in file and "reverse" not in file:
            continue

        #Go through the file, creating a DataFrame for every 130 lines
        i = 0
        while True:
            try:
                cycle = find_cycle(file, i)
            
                if cycle % 30 == 0:
                    table = pd.read_table(file, skiprows=1+i)
                    df = pd.DataFrame(table)
                    mean = df["Friction Coeff."].head(65).astype(float)

                    #Average the Frictional Coeff. column to 9 decimal places
                    avg = round(mean.mean(), 9)

                    #Separate into forward and reverse arrays by reading filenames
                    if "forward" in file.split("\\")[-1]:
                        forward.append(avg)
                    else:
                        reverse.append(avg)
                
                i += 130
            except:
                break

    frictional_offset = [statistics.mean(forward), statistics.mean(reverse)]
    frictional_offset = statistics.mean(frictional_offset)
    print("\nTest ID: ", id)
    print("Frictional Offset: ", frictional_offset, "\n")
    return frictional_offset

list_of_files = find_files_of_type("xls")
test_ids = find_test_ids(list_of_files)
for id in test_ids:
    if "D" in id:
        for file in list_of_files:
            if id in file:
                
                #Select only the test file
                if "forward" in file or "reverse" in file:
                    continue

                test_cycles_and_values = {}
                i = 0
                while True:
                    for j in range(0,5):
                        try:
                            cycle = find_cycle(file, i)

                            test_df = pd.read_table(file, skiprows=i+1)
                            df = pd.DataFrame(test_df)
                            
                            torque_average = []
                            for k in range(59, 70):
                                average.append(float(df.iloc[k]["Friction Torque"]))

                            friction_average = []
                            for k in range(59, 70):
                                average.append(float(df.iloc[k]["Friction Coeff."]))
                                
                            print(statistics.mean(average))

                            test_cycles_and_values[cycle] = abs(statistics
                                                                .mean(average) - frictional_offset)
                            i += 130
                        except:
                            break
    else:
        frictional_offset = find_frictional_offset(list_of_files, id)

        for file in list_of_files:
            if id in file:

                #Select only the test file
                if "forward" in file or "reverse" in file:
                    continue

                test_numbers_and_values = {}
                i = 0

                while True:
                    try:
                        test_number = find_cycle(file, i)

                        if test_number % 30 == 0:
                            test_df = pd.read_table(file, skiprows=i+1)
                            df = pd.DataFrame(test_df)

                            average = []
                            for j in range(59, 70):
                                average.append(float(df.iloc[j]["Friction Coeff."]))

                            print(statistics.mean(average))

                            test_numbers_and_values[test_number] = abs(statistics.mean(average) - frictional_offset)
                        i += 130
                    except:
                        break

            (pd.DataFrame.from_dict(data=test_numbers_and_values, orient='index')
            .to_csv(id+".csv", header=False))
            print("\n====================\n")

