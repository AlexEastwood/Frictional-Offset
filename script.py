import os
import re
import sys
import statistics
import pandas as pd
import matplotlib.pyplot as plt


# Set path to the current directory of the python script
# Find all files in current and child directories of the chosen extension
def find_files_of_type(type):
    path = sys.path[0]
    list_of_files = []
    for root, dirs, files in os.walk(path):
        for file in files:
            if file.endswith("." + type):
                list_of_files.append(os.path.join(root, file))
    return list_of_files


# Use regex to find all unique pig and degree test IDs in all files
def find_test_ids(list_of_files):
    ids = []
    for file in list_of_files:
        m = re.match(r"(.*)(_P\d+_|_\d+D_)(.*)", file)
        if m:
            if m.group(2) not in ids:
                ids.append(m.group(2))
    for file in list_of_files:
        m = re.match(r"(.*)(\w{2}ANK.*)(.xls)", file)
        if m:
            if "forward" in file or "reverse" in file:
                m = re.match(r"(.*)(\w{2}ANK.*)(_forward.*|_reverse.*)", file)
                if m.group(2) not in ids:
                    ids.append(m.group(2))
            else:
                ids.append(m.group(2))
                
    return ids


# The cycle number is above and to the left of each table of data, this
# function is used to find it so the row underneath can be used as the index in the dataframe
def find_cycle(file, i):
    columns = pd.read_table(file, skiprows=i)
    df = pd.DataFrame(columns)
    cycle = int(''.join(c for c in str(df.columns)
                        .split(",")[1] if c.isdigit()))
    return cycle

# Groups values into sets of 5 and averages each set, then averages them all
# together and appends that mean value to the end of the list
def find_averages(list_name):
    average_list = []
    for i in range(0, len(list_name), 5):
        average_list.append(statistics.mean(list_name[i:i+5]))
    average_list.append(statistics.mean(average_list))
    return average_list


def degree(id, list_of_files):
    if not os.path.exists("degrees"):
        os.makedirs('degrees')
        path = sys.path[0] + "\\degrees"
    else:
        path = sys.path[0] + "\\degrees"

    # Create dataframe containing the required index and column names
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

    # For each column in the dataframe, fill with list of averages
    final_df["Forward Friction"] = find_averages(forward_friction)
    final_df["Forward Torque"] = find_averages(forward_torque)
    final_df["Reverse Friction"] = find_averages(reverse_friction)
    final_df["Reverse Torque"] = find_averages(reverse_torque)

    # Average the relevant cells for each row in the dataframe and add to
    # the "Average Torque" and "Friction Coeff." columns
    final_df["Average Torque"] = final_df.apply(
        lambda row: statistics.mean(
            [row["Forward Torque"], abs(row["Reverse Torque"])]), axis=1)
    final_df["Friction Coeff."] = final_df.apply(
        lambda row: statistics.mean(
            [row["Forward Friction"], abs(row["Reverse Friction"])]), axis=1)

    final_df.to_csv(os.path.join(path, id+".csv"))
    print(id + ".csv created!")

def find_frictional_offset(list_of_files, id):
    forward = []
    reverse = []

    for file in list_of_files:
        # Ignore files that are not relevant to the current ID, or the actual
        # test file since the frictional coefficient is found just using
        # the "forward" and "reverse" files
        if id not in file:
            continue
        if "forward" not in file and "reverse" not in file:
            continue

        # Go through the file, creating a DataFrame for every 130 lines
        i = 0
        while True:
            try:
                cycle = find_cycle(file, i)

                # Only using cycles 30, 60, 90, etc.
                if cycle % 30 == 0:
                    table = pd.read_table(file, skiprows=1+i)
                    df = pd.DataFrame(table)
                    mean = df["Friction Coeff."].head(65).astype(float)

                    # Average the Frictional Coeff. column to 9 decimal places
                    avg = round(mean.mean(), 9)

                    # Separate into forward and reverse arrays by reading filenames
                    if "forward" in file.split("\\")[-1]:
                        forward.append(avg)
                    else:
                        reverse.append(avg)

                i += 130
            except:
                break
    
    # Average all values together to get frictional offset
    frictional_offset = [statistics.mean(forward), statistics.mean(reverse)]
    frictional_offset = statistics.mean(frictional_offset)

    return frictional_offset

list_of_files = find_files_of_type("xls")
test_ids = find_test_ids(list_of_files)
id_diameter = {"_P1_": 36, "_P4_": 31, "_P6_": 33, "_P7_": 30, "_P10_": 35}
human_id_diameter = pd.read_excel("A_Canden_Human_Tissue_Testing_Plan.xlsx")
human_id_diameter = human_id_diameter.set_index("Sample ID").to_dict()["Diameter of talus"]

for id in test_ids:
    
    if "D_" in id:
        continue
        degree(id, list_of_files)
    elif "ANK" in id:
        if not os.path.exists("humans"):
            os.makedirs('humans')
        path = sys.path[0] + "\\humans"
        
        print(id)
        frictional_offset = find_frictional_offset(list_of_files, id)
        
        for file in list_of_files:
            if id in file:

                # Select only the test file
                if "forward" in file or "reverse" in file:
                    continue

                for s in human_id_diameter.keys():
                    if s in id:
                        diameter = human_id_diameter[s]
                        break
                    
                test_numbers_and_values = {}
                i = 0

                while True:
                    try:
                        test_number = find_cycle(file, i)

                        if test_number < 1000:
                            if test_number % 30 == 0:
                                test_df = pd.read_table(file, skiprows=i+1)
                                df = pd.DataFrame(test_df)

                                average = []
                                for j in range(59, 70):
                                    average.append(float(df.iloc[j]["Friction Torque"]))
                                    
                                radius = (diameter/2) / 10**3

                                test_numbers_and_values[test_number] = abs(
                                    (statistics.mean(average) / (radius * 640)) - frictional_offset)
                            i += 130
                        else:
                            if test_number % 50 == 0:
                                test_df = pd.read_table(file, skiprows=i+1)
                                df = pd.DataFrame(test_df)

                                average = []
                                for j in range(59, 70):
                                    average.append(float(df.iloc[j]["Friction Torque"]))
                                    
                                radius = (diameter/2) / 10**3

                                test_numbers_and_values[test_number] = abs(
                                    (statistics.mean(average) / (radius * 640)) - frictional_offset)
                            i += 130
                    except:
                        break

                print("Creating: ", id, ".csv")
                (pd.DataFrame.from_dict(data=test_numbers_and_values, orient='index')
                 .to_csv(os.path.join(path, id+".csv"), header=False))
    
    else:
        continue
        if not os.path.exists("oinkers"):
            os.makedirs('oinkers')
        path = sys.path[0] + "\\oinkers"

        frictional_offset = find_frictional_offset(list_of_files, id)

        for file in list_of_files:
            if id in file:

                # Select only the test file
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
                                average.append(float(df.iloc[j]["Friction Torque"]))
                                
                            radius = (id_diameter[id]/2) / 10**3

                            test_numbers_and_values[test_number] = abs(
                                (statistics.mean(average) / (radius * 640)) - frictional_offset)
                        i += 130
                    except:
                        break

                (pd.DataFrame.from_dict(data=test_numbers_and_values, orient='index')
                 .to_csv(os.path.join(path, id+".csv"), header=False))
                print("\n====================\n")

exit()
for id in test_ids:
    if "D" in id:
        for file in list_of_files:
            if id in file and "fowards" in file:
                i = 0
                while True:
                    try:
                        test_number = find_cycle(file, i)

                        if test_number == 90:
                            test_df = pd.read_table(file, skiprows=i+1)
                            df = pd.DataFrame(test_df)
                            
                            index = df["Index"].head(128).tolist()
                            index = [int(j) for j in index]
                            motor_position = df["Motor Position"].head(128).tolist()
                            motor_position = [float(j) for j in motor_position]
                            
                            plt.axes().spines["bottom"].set_position(("data", 0))
                            plt.scatter(index, motor_position)
                            plt.show()
                            exit()
                        
                        i += 130
                    except:
                        break
                