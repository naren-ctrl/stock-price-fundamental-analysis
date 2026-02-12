import pandas as pd
file_path = r"E:\stock-analysis-assignment\Intern test 2 - correlation regression - Copy.xls"

print('Reading Sheet2 with header=1')
df = pd.read_excel(file_path, sheet_name='Sheet2', header=1)
print('\nShape:', df.shape)
print('\nColumns:')
print(df.columns.tolist())
print('\n--- head (first 10 rows) ---')
print(df.head(10).to_string())
print('\n--- first 12 rows, first 12 cols (raw) ---')
print(df.iloc[:12, :12].to_string())

# show column 4 onwards sample
print('\n--- column labels 4: ---')
print(df.columns[4:15].tolist())

# show row 0..6 values for cols 4:
print('\n--- rows 0..6, cols 4: ---')
print(df.iloc[0:7, 4:15].to_string())
