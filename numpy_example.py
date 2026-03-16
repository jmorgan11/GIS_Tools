"""NumPy examples."""
import numpy as np

# 1D Array
a = np.array([0, 1, 2, 3])
print("1d Array:", a)
print("Dimension:", a.ndim)
print("Length:", len(a))

print("\n")

# 2D Array
b = np.array([[0, 1, 2, 3], [4, 5, 6, 7], [8, 9, 10, 11]])
print("2D Array:", b)
print("Dimension:", b.ndim)
print("Length:", len(b))
print("Shape:", b.shape)

print("\n")

# 3D Array
c = np.array(
    [
        [
            [1],
            [2],
            [3],
        ],
        [
            [4],
            [5],
            [6]
        ]
    ]
)
print("3D Array:", c)
print("Dimension:", c.ndim)
print("Length:", len(c))
print("Shape:", c.shape)

print("\n")

# 2D Coordinate Array
newarray = np.array([(1, (471316, 5130448)), (2, (470402, 5130249))], dtype=object)
print("2D Coordinate Array:", newarray)

print("\n")

# All Zero Array
zeroarray = np.zeros((3, 5))
print("Zero Array:", zeroarray)

print("\n")

# Range Array
newarray = np.arange(1, 10)
print("Range Array:", newarray)

print("\n")

# Reshape an Array
array3x3 = np.arange(1, 10).reshape((3, 3))
print("Reshaped Array:", array3x3)
