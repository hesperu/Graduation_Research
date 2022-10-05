"""
な　に　こ　れ　笑？
sldem2015のimgファイルをtif,pngへ変換するスクリプト
一括で変換するよ
"""
import pathlib
import numpy as np
import re
import tifffile
import matplotlib.pyplot as plt

# lblファイルを読み込んで,メタデータを抽出する
def extract_lbl_file(data_path):
    lbl_list = data_path.glob('**/*.LBL')

    #lblファイルを一括で読み込み
    extract_list = []
    """
    正規表現でlblから情報取ってくる
    必要となる情報は、
    ・SAMPLE_TYPE: 画素のタイプについて(intとかfloatとか、ビッグエンディアンとか)
    ・LINES:画像の縦方向の画素数
    ・LINE_SAMPLES:画像の横方向の画素数
    ・FILE_NAME:ファイルの名前
    ・SAMPLE_BITS:位置画素あたり何bitか？
    """
    lbl_set = set(["SAMPLE_TYPE","LINES","LINE_SAMPLES","FILE_NAME","SAMPLE_BITS"])

    for lbl in lbl_list:
        with open(lbl) as l:
            lbl_value = {}
            lbl_name = ""
            while True:
                l_line = l.readline()
                if not l_line:
                    break
                else:
                    # lblファイルは馬鹿みたいに空白が多いから取り除く
                    # ダブルクォーテーションは邪魔だから消す
                    splited_line = re.split("\s+",l_line.replace('"',''))
                    splited_line.remove('')
                    if splited_line[0] in lbl_set:
                        lbl_value[splited_line[0]] = splited_line[2]

            extract_list.append(lbl_value)
    
    return extract_list

# lblから読み込んだメタデータをpython内部でつけるように変換する
# lblから読み込んだデータが入っているリストを引数に取る
def convert_metadata(lbl_list):
    for i,lbl in enumerate(lbl_list):
        for key in lbl.keys():
            if key == "LINES" or key == "LINE_SAMPLES" or key == "SAMPLE_BITS":
                lbl_list[i][key] = int(lbl_list[i][key])
        # ここでデータ型を決める。条件分岐がめんどい。なんかいい方法ないかな？
        if lbl["SAMPLE_TYPE"] == "PC_REAL" and lbl["SAMPLE_BITS"] == 32:
            lbl_list[i]["PYTHON_DATA_TYPE"] = "f4"

    return lbl_list

# imgをtiffとpngに変換する
# 下処理済みのメタデータが入っている配列と、親ディレクトリを引数にとる
def img2tiffpng(lbl_list,data_path):
    for lbl in lbl_list:
        print(lbl)
        file_name = lbl["FILE_NAME"]
        file_path = data_path.joinpath(file_name)
        img = np.fromfile(file_path,dtype=lbl["PYTHON_DATA_TYPE"])
        LINES = lbl["LINES"]
        LINE_SAMPLES = lbl["LINE_SAMPLES"]
        img = img.reshape(LINES,LINE_SAMPLES)

        tiff_path = file_path.with_suffix('.tif')
        tifffile.imwrite(tiff_path,img)

        png_path = file_path.with_suffix('.png')
        plt.imsave(png_path,img,cmap='gray')

if __name__ == '__main__':
    # データは研究室のPCにおいてあるやつを使う
    # 家で使いたいなら外付けのssdに入れといて
    data_path = pathlib.Path('/','mnt','ssd4T','ibuka_dataset','origin','sldem')
    lbl_list = convert_metadata(extract_lbl_file(data_path))
    img2tiffpng(lbl_list,data_path)
