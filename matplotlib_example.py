"""Using Matplotlib examples."""
import matplotlib.pyplot as plt
import numpy as np


# Create a scatterplot of five points using green circles
plt.plot(
    [1, 2, 3, 4, 5],
    [2, 4, 3, 5, 4],
    "go"
    )

# Adjust axis
plt.axis([0, 6, 0, 6])

# Change axis labels
plt.xlabel("variable x")
plt.ylabel("variable y")

plt.show()

# Save it as figure
plt.savefig("demoplot.png")
