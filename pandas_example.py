"""Working with Pandas"""
import pandas as pd

# Read a CSV
df = pd.read_csv("C:\Temp\Documents\GIS\Data\people_data.csv")

# Print the first few rows
print(df.head(2))

# Print the last few rows
print(df.tail(2))

# Print a random sample
print(df.sample(2))

# Work with only a few columns
small_df = df[["Last Name", "Job Title"]]
print(small_df.head(2))

# Change order of columns
new_df = df[["Job Title", "First Name", "Last Name"]]
print(new_df.head(2))

# Select only one column and creating a Pandas Series
titles = df["Job Title"]
print(titles.head())