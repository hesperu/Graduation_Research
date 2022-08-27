import numpy as np
import matplotlib.pyplot as plt

data = np.fromfile('SLDEM2015_256_0N_60N_000_120_FLOAT.IMG','i4')

LINES = 15360
LINE_SAMPLES = 30720

img = data.reshape(LINES,LINE_SAMPLES)
plt.imshow(img,cmap='gray')
plt.show()