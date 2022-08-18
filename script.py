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
        m = re.match(r"(.*)(_P\d+_|_\d+D_)(.*)", file)
        if m.group(2) not in ids:
            ids.append(m.group(2))
    return ids

def find_cycle(file, i):
    columns = pd.read_table(file, skiprows=i)
    df = pd.DataFrame(columns)
    cycle = int(''.join(c for c in str(df.columns)
                        .split(",")[1] if c.isdigit()))
    return cycle

def find_averages(list_name):
            average_list = []
            for i in range(0, len(list_name), 5):
                average_list.append(statistics.mean(list_name[i:i+5]))
            average_list.append(statistics.mean(average_list))
            return average_list

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
        final_df = pd.DataFrame(index=["30-34",
                                       "60-64", 
                                       "90-94", 
                                       "120-124",
                                       "Mean"], 
                                columns=["Forward Torque", 
                                        "Forward Friction", 
                                        "Reverse Torque", 
                                        "Reverse Friction", 
                                        "Average Torque", 
                                        "Friction Coeff."])
        
        forward_friction = []
        forward_torque = []
        reverse_friction = []
        reverse_torque = []
        
        for file in list_of_files:
            if id in file:

                i = 0
                while True:
                    try:
                        test_df = pd.read_table(file, skiprows=i+1)
                        df = pd.DataFrame(test_df)
                        
                        torque_average = []
                        for k in range(59, 70):
                            torque_average.append(float(df.iloc[k]["Friction Torque"]))

                        friction_average = []
                        for k in range(59, 70):
                            friction_average.append(float(df.iloc[k]["Friction Coeff."]))
                        
                        if "fowards" in file:
                            forward_friction.append(statistics.mean(friction_average))
                            forward_torque.append(statistics.mean(torque_average))
                        else:
                            reverse_friction.append(statistics.mean(friction_average))
                            reverse_torque.append(statistics.mean(torque_average))
                        i += 130
                    except:
                        break
        
        
        final_df["Forward Friction"] = find_averages(forward_friction)
        final_df["Forward Torque"] = find_averages(forward_torque)
        final_df["Reverse Friction"] = find_averages(reverse_friction)
        final_df["Reverse Torque"] = find_averages(reverse_torque)
        print(final_df)

    else:
        continue
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

