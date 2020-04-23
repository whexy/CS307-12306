import matplotlib.pyplot as plt
import numpy as np

x = [15, 52, 104, 175, 200, 231, 261, 281, 374, 402, 418, 448, 508, 530, 550, 550]
y = [8, 54, 110, 211, 244, 281, 307, 324, 434, 458, 471, 502, 570, 586, 598, 598]
k, b, _ = np.polyfit(x, y, 1)
print(k, b)
plt.plot(x, y)
plt.show()
