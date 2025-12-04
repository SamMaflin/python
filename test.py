# read cv 
import pandas as pd
import numpy as np

df = pd.read_csv('analysis/Final_Task_Data.csv')
# FIND UNQIUE LEAGUES 
leagues = df['League'].unique().tolist()
print(leagues)




