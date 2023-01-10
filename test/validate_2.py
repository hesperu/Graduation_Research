from PIL import Image
import numpy as np
import math
import scipy.ndimage
import matplotlib.pyplot as plt

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

def calc_mae(img1:Image,img2:Image):
    if img1.size != img2.size:
        print("二つの画像のピクセル数が違うよ!")
    height = img1.height
    width = img2.width
    img1 = np.asarray(img1)
    img2 = np.asarray(img2)

    pixel_count = height * width
    mae = sum([abs(int(pix1) - int(pix2)) for pix1,pix2 in zip(img1.flatten(),img2.flatten())]) / pixel_count

    return mae

def lineprofile(vis:Image,generated:Image,real:Image):
    x0,y0 = 0,215
    x1,y1 = 255,180
    num = int(round(np.hypot(x1-x0, y1-y0))) #二点間の距離をピクセル数に変換
    x, y = np.linspace(x0, x1, num), np.linspace(y0, y1, num)

    if x1-x0 == 0:# This type of Lines is parallel to y-axis
        factorx = 1
        factory = 0
    elif y1-y0 == 0:# This type of Lines is parallel to x-axis
        factorx = 0
        factory = 1
    else:# Evaluate the slops of the line and the orthogonal one...
        a = (y1-y0)/(x1-x0)
        inv_a = - 1/a
        factor = pow(pow(a,2)/(pow(a,2)+1),1/2)
        factorx = factor
        factory = inv_a*factor

    """
    線に沿ったピクセル値を補完しつつ取得
    """
    DEM_RANGE = [1915.1011,4493.9414]
    pixel_resolution = 55.0

    generated = np.array(generated)
    generated = (generated - generated.min())/(generated.max() - generated.min())
    generated = (generated*DEM_RANGE[1] - generated*DEM_RANGE[0]+DEM_RANGE[0])

    real = np.array(real)
    real = (real - real.min())/(real.max() - real.min())
    real = (real*DEM_RANGE[1] - real*DEM_RANGE[0]+DEM_RANGE[0])

    z1 = scipy.ndimage.map_coordinates(generated,np.vstack((x,y)))
    z2 = scipy.ndimage.map_coordinates(real,np.vstack((x,y)))

    """
    ラインプロファイルの線の太さはデフォルトでは1px
    これを変えた時は次の処理が必要
    SumZ = z1/(int(width/2)*2+1)
    for i in range(1,int(width/2)+1):
        zi = scipy.ndimage.map_coordinates(z, np.vstack((x+round(i*factorx),y+round(i*factory))))
        SumZ = SumZ + zi/(int(width/2)*2+1)
        zi = scipy.ndimage.map_coordinates(z, np.vstack((x-round(i*factorx),y-round(i*factory))))
        SumZ = SumZ + zi/(int(width/2)*2+1)
    avZ = SumZ
    """
    plt.figure(figsize=(12,9))
    plt.subplot(2,3,1)
    plt.plot([x0, x1], [y0, y1], 'go-',linewidth = 1)
    plt.imshow(vis,cmap="gray")
    plt.subplot(2,3,2)
    plt.imshow(generated,cmap="gray")
    plt.plot([x0, x1], [y0, y1], 'ro-',linewidth = 1)
    plt.subplot(2,3,3)
    plt.imshow(real,cmap="gray")
    # plt.plot([x0, x1], [y0, y1], 'ro-',linewidth = width,label='width='+str(width))
    plt.plot([x0, x1], [y0, y1], 'bo-',linewidth = 1)
    plt.legend()
    plt.subplot(2,1,2)
    plt.rcParams["font.size"] = 18
    x_values = [x*pixel_resolution if x ==0 or x == int(num/2) or x == num-1 else "" for x in range(int(num))]
    x = [int(x) for x in range(num)]
    plt.xticks(x,x_values)
    plt.tick_params(labelsize=18)
    plt.plot(z1,'r',label="Generated DEM")
    plt.plot(z2,'b',label="LRO NAC DEM")
    plt.ylim(DEM_RANGE[0]-100,DEM_RANGE[1]+500)
    # plt.plot(avZ,label='width='+ str(width))
    plt.legend()
    plt.xlabel('Distance(m)')
    plt.ylabel('Height (m)')

    plt.savefig("result_2.tiff")

    

if __name__ == "__main__":
    import sys
    img1 = Image.open(sys.argv[1]).convert("L")
    img2 = Image.open(sys.argv[2]).convert("L")
    img3 = Image.open(sys.argv[3]).convert("L")
    """
    print(calc_rmse(img1,img2))
    print(calc_mae(img1,img2))
    """
    lineprofile(img1,img2,img3)