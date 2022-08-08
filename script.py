import os
import re
import sys
import statistics
import pandas as pd

#Set path to the current directory of the python script
path = sys.path[0]

#Find all .csv files in current and child directories
list_of_files = []
for root, dirs, files in os.walk(path):
    for file in files:
        if file.endswith(".xls"):
            list_of_files.append(os.path.join(root, file))

test_numbers = []
for file in list_of_files: 
    m = re.match(r"(.*)(_P\d+_)(.*)", file)
    if m.group(2) not in test_numbers:
        test_numbers.append(m.group(2))

#Create arrays to store average coeffs in each file going forward or reverse
forward = []
reverse = []


for file in list_of_files:

    #Ignore the test file
    if "forward" not in file and "reverse" not in file:
        continue

    csv_avg = []
    filename = file
    #Go through the csv file, creating a DataFrame for every 130 lines
    for i in range(0, 520, 130):
        file = pd.read_excel(filename, engine='openpyxl')
        df = pd.DataFrame(file)
        mean = df["Friction Coeff."].head(65).astype(float)

        #Average the Frictional Coeff. column to 9 decimal places
        csv_avg.append(round(mean.mean(), 9))

        #Separate into forward and reverse arrays by reading filenames
        if "forward" in filename.split("\\")[-1]:
            forward.append(round(mean.mean(), 9))
        else:
            reverse.append(round(mean.mean(), 9))


frictional_offset = [statistics.mean(forward), statistics.mean(reverse)]
frictional_offset = statistics.mean(frictional_offset)

print("\nFrictional Offset: ", frictional_offset, "\n")
for file in list_of_files:

    #Ignore the test file
    if "forward" in file or "reverse" in file:
        continue

    test_numbers_and_values = {}
    i = 0

    while True:
        try:

            columns = pd.read_csv(file, skiprows=i*130)
            df = pd.DataFrame(columns)
            test_number = df.columns[1]
            if int(test_number) % 30 != 0:
                i += 1
                continue

            test_df = pd.read_csv(file, skiprows=i*130+1)
            df = pd.DataFrame(test_df)

            average = []
            for j in range(59, 70):
                average.append(float(df.iloc[j]["Friction Coeff."]))

            print(statistics.mean(average))

            test_numbers_and_values[test_number] = abs(statistics.mean(average) - frictional_offset)
            i += 1
        except:
            break

#(pd.DataFrame.from_dict(data=test_numbers_and_values, orient='index')
# .to_csv('dict_file.csv', header=False))
