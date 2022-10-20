import numpy as np
from osgeo import gdal, gdalconst, gdal_array


# tifの読み込み (read only)
src = gdal.Open('geotif.tif',gdalconst.GA_ReadOnly)
print(type(src))

print(src.RasterXSize) # 水平方向ピクセル数
print(src.RasterYSize) # 鉛直方向ピクセル数
print(src.RasterCount) # バンド数

band = src.GetRasterBand(1).ReadAsArray()
print(band)

# 型番号 (ex: 6 -> numpy.float32)、こやつがnumpyに変換するための鍵となる。
dtid = src.GetRasterBand(1).DataType
print(dtid)

# 型番号 -> 型名 変換
gdal_array.GDALTypeCodeToNumericTypeCode(dtid) 
print(gdal_array.GDALTypeCodeToNumericTypeCode(dtid))

# ファイル名
src.GetDescription() 
src.GetGeoTransform() 
"""
座標に関する６つの数字を入手する
[始点端x座標（経度）,
x方向（西東）解像度,
回転,
始点端y座標（緯度）,
回転,
y方向（南北）解像度（北南方向であれば負）] 。

"""
src.GetProjection() # 座標系情報

"""
メタデータの情報を会得する
"""

src.GetMetadata() # 辞書型のメタデータ配列
src.GetMetadataItem('itemname') # 項目指定 (ex: 'TIFFTAG_XRESOLUTION', 'TIFFTAG_DATETIME', ..)


"""
他にも色々あるからドキュメントを読もうね
"""