from PIL import Image
import numpy as np
import math


def alignment_MI(img1:Image,img2:Image):
    X = 256 #DTMの横ピクセル
    Y = 256 #DTMの縦ピクセル
    
    histgramX = 256
    histgramY = 256

    img1_pix = np.asarray(img1)
    max_mi = 0
    #縦と横に一ピクセルずつ可視画像をずらす
    result_img = None
    for h in range(0,img2.height-Y):
        for w in range(0,img2.width-X):
            cut_img2 = img2.crop((h,w,256+h,256+w))
            img2_pix = np.asarray(cut_img2)

            histmap = [[0 for j in range(histgramX)] for i in range(histgramY)]
            p_ab = [[0 for j in range(histgramX)] for i in range(histgramY)]
            p_a = [0 for j in range(histgramX)]
            p_b = [0 for i in range(histgramY)]
            t = [[0 for j in range(histgramX)] for i in range(histgramY)]

            histsum = 0
            #二次元ヒストグラムの作成
            #出現した数の回数を数える
            mutual = 0
            
            img1_pix = img1_pix.flatten()
            img2_pix = img2_pix.flatten()

            for k in range(len(img1_pix)):
                num1 = img1_pix[k]
                num2 = img2_pix[k]
                histmap[num1][num2] += 1
            
            for m in range(histgramX):
                for n in range(histgramY):
                    histsum += histmap[m][n]
            
            #相互情報量計算
            
            #p(a,b)
            for m in range(histgramX):
                for n in range(histgramY):
                    p_ab[m][n] = histmap[m][n] / (1.0*histsum) #1.0でかけるのはfloatにするため

            #p(a),p(b)
            for m in range(histgramX):
                for n in range(histgramY):
                    p_a[m] += p_ab[m][n]
                    p_b[n] += p_ab[m][n]

            for m in range(histgramX):
                for n in range(histgramY):
                    if p_a[m]*p_b[n] != 0:
                        t[m][n] = p_ab[m][n]/(1.0*p_a[m]*p_b[n])
                        if t[m][n] != 0:
                            mutual += p_ab[m][n]*math.log(t[m][n],2)

            if mutual > max_mi:
                max_mi = mutual
                result_img = cut_img2
            
            print("最大情報量:{mi}, 今計算した情報量{cur}".format(mi=max_mi,cur=mutual))

    new_img = Image.new("L",(512,256),(255))
    new_img.paste(img1,(0,0))
    new_img.paste(result_img,(256,0))
    new_img.save("result.tiff")

if __name__ == "__main__":
    import sys
    if len(sys.argv) < 3:
        print("画像が指定されていない")
    img1 = Image.open(sys.argv[1])
    img2 = Image.open(sys.argv[2])
    alignment_MI(img1,img2)