"""Using Matplotlib to plot sea level rise."""
import matplotlib.pyplot as plt
import pandas as pd

# Open the CSV
df = pd.read_csv(r"C:\GIS\Data\CSIRO_Alt_yearly.csv")

# Get the first few records
print(df.head())

# Get the columns needed
year = df["Time"]
sea_levels = df["GMSL (yearly)"]

# Create the plot
plt.plot(year, sea_levels, "ro", markersize=2.0)

# Label the axis
plt.xlabel("Year")
plt.ylabel("Sea Level (inches)")

# Label the title
plt.title("Rise in Sea Level")

# Show the plot
plt.show()

# Save the plot
plt.savefig("sealevel.png")
