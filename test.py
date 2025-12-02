import pandas as pd

# Load CSV
data = pd.read_csv(r'C:\Users\SMafl\python\Final_Task_Data.csv')

# Unique values from both columns
positions_1 = data['Position_1'].dropna().unique()
positions_2 = data['Position_2'].dropna().unique()

# Combine into a single set of unique positions
all_positions = sorted(set(positions_1).union(set(positions_2)))

print("All possible positions:")
for pos in all_positions:
    print(pos)
