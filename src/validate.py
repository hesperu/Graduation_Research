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

def lineprofile(img:Image):
    x0,y0 = 12, 12.5
    x1,y1 = 60,255

    line_pix_num = int(round(np.hypot(x1-x0, y1-y0))) #二点間のピクセル数に変換
    x,y = np.linspace(x0,x1,line_pix_num), np.linspace(y0,y1,line_pix_num)

    """
    横、縦どちらかに垂直な線を引く場合は0で破らないようにする
    """
    if x1-x0 == 0:
        factorx = 1
        factory = 0
    elif y1-y0 == 0:
        factorx = 0
        factory = 1
    else:
        """
        n pixelだけ平行移動した直線のx,y座標はfactorを用いて計算
        """
        a = (y1-y0)/(x1-x0)
        inv_a = -1/a
        factor = pow(pow(a,2)/(pow(a,2)+1),1/2)
        factorx = factor
        factory = inv_a*factor

    """
    線に沿ったピクセル値を補完しつつ取得
    """
    z1 = scipy.ndimage.map_coordinates(np.asarray(img),np.vstack((x,y)))

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
    plt.subplot(2,1,1)
    plt.imshow(img,cmap="gray")
    # plt.plot([x0, x1], [y0, y1], 'ro-',linewidth = width,label='width='+str(width))
    plt.plot([x0, x1], [y0, y1], 'bo-',linewidth = 1, label='width=1')
    plt.legend()
    
    plt.subplot(2,1,2)
    plt.rcParams["font.size"] = 18
    plt.tick_params(labelsize=18)
    plt.plot(z1,label='width=1')
    # plt.plot(avZ,label='width='+ str(width))
    plt.legend()
    plt.xlabel('pixel')
    plt.ylabel('hight')

    plt.savefig("result.tiff")

    

if __name__ == "__main__":
    import sys
    img1 = Image.open(sys.argv[1])
    img2 = Image.open(sys.argv[2])

    print(calc_rmse(img1,img2))
    print(calc_mae(img1,img2))
    lineprofile(img2)
