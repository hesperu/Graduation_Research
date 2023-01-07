import numpy as np
from matplotlib import pyplot as plt
from PIL import Image
Image.MAX_IMAGE_PIXELS = 1000000000

np.random.seed(0)

img = np.array(Image.open("/Users/koichiro/University/research/Graduation_Research/test/HPONDS/7805.tiff") )

print(img.dtype)
print(img)
print(img.min(),img.max())
fig, ax = plt.subplots()
ax.imshow(img, cmap="gray")
plt.show()
