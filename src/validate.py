from PIL import Image
import numpy as np
import math

def calc_rmse(img1:Image,img2:Image):
    """
    """
    if img1.size != img2.size:
        print("二つの画像のピクセル数が違うよ!")
    height = img1.height
    width = img1.width
    img1 = np.asarray(img1)
    img2 = np.asarray(img2)

    pixel_count = height*width
    print(img1.shape)
    mse = sum([(int(pix1)-int(pix2))*(int(pix1)-int(pix2)) for pix1,pix2 in zip(img1.flatten(),img2.flatten())]) / pixel_count
    rmse =  math.sqrt(mse)

    return rmse

if __name__ == "__main__":
    import sys
    img1 = Image.open(sys.argv[1])
    img2 = Image.open(sys.argv[2])

    print(calc_rmse(img1,img2))
