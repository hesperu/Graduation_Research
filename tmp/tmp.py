import numpy as np
import matplotlib.pyplot as plt

data = np.fromfile('DTM_MAP_01_N00E000S01E001SC.IMG',dtype='>i2')

BANDS = 1
LINES = 4096
LINE_SAMPLES = 4096
OFFSET = 0.000000

img = data.reshape(BANDS,LINE_SAMPLES,LINES)
plt.imshow(img[0],cmap='gray')
plt.show()