import csv
import os
import sys
import statistics
import pandas as pd
from num2words import num2words


#Set path to the current directory of the python script
path = sys.path[0]

#Find all .csv files in current and child directories
list_of_files = []
for root, dirs, files in os.walk(path):
    for file in files:
        if file.endswith(".csv"):
            list_of_files.append(os.path.join(root, file))

#Create arrays to store average coeffs in each file going forward or reverse
forward = []
reverse = []
print("\n\n")

for file in list_of_files:

    #Ignore the test file
    if "forward" not in file and "reverse" not in file:
        continue

    csv_avg = []
    filename = file
    print(filename.split("\\")[-1])
    j = 30
    #Go through the csv file, creating a DataFrame for every 130 lines
    for i in range(0, 520, 130):
        file = pd.read_csv(filename, skiprows=1+i)
        df = pd.DataFrame(file)
        mean = df["Friction Coeff."].head(65).astype(float)

        #Average the Frictional Coeff. column to 9 decimal places
        csv_avg.append(round(mean.mean(), 9))

        #Separate into forward and reverse arrays by reading filenames
        if "forward" in filename.split("\\")[-1]:
            forward.append(round(mean.mean(), 9))
        else:
            reverse.append(round(mean.mean(), 9))

        test_number = num2words(j)
        j += 30

        print(test_number, "avg. friction coeff:", round(mean.mean(), 9))

    print("\navg. coeff of file", statistics.mean(csv_avg))
    print("\n==========\n")


frictional_offset = [statistics.mean(forward), statistics.mean(reverse)]
frictional_offset = abs(statistics.mean(frictional_offset))

print("Frictional Offset: ", frictional_offset)

for file in list_of_files:

    #Ignore the test file
    if "forward" in file or "reverse" in file:
        continue

    test_numbers_and_values = {}
    i = 0

    while True:
        try:
            columns = pd.read_csv(file, skiprows=i)
            df = pd.DataFrame(columns)
            test_number = (num2words(df.columns[1]))

            test_df = pd.read_csv(file, skiprows=i+1)
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
   .to_csv('dict_file.csv', header=False))