import os
import sys
import pandas as pd
from num2words import num2words
import statistics

#Set path to the current directory of the python script
path = sys.path[0]

#Find all .csv files in current and child directories
list_of_files = []
for root, dirs, files in os.walk(path):
	for file in files:
	  if file.endswith(".csv"):
		  list_of_files.append(os.path.join(root,file))
		  
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
    else :
      reverse.append(round(mean.mean(), 9))
      
    test_number = num2words(j)
    j += 30
      
    print(test_number, "avg. friction coeff:", round(mean.mean(), 9))
    
  print("\navg. coeff of file", statistics.mean(csv_avg))
  print("\n==========\n")
  
  
frictional_offset = [statistics.mean(forward), statistics.mean(reverse)]  

print("Frictional Offset: ",statistics.mean(frictional_offset))



