import os
import sys
import statistics
import pandas as pd

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


for file in list_of_files:

    #Ignore the test file
    if "forward" not in file and "reverse" not in file:
        continue

    csv_avg = []
    filename = file
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
            
        j += 30

frictional_offset = [statistics.mean(forward), statistics.mean(reverse)]
frictional_offset = statistics.mean(frictional_offset)

print("Frictional Offset: ", frictional_offset)
exit()
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
            test_number = df.columns[1]

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
