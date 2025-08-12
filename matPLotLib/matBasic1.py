import matplotlib.pyplot as plt

x = [1, 2, 3, 4]
y = [3, 5, 7, 9]
plt.grid(True)
plt.xlabel("X")
plt.ylabel("Y")
plt.title("graph")
plt.plot(x, y, "r-*", linewidth=3)
plt.show()
