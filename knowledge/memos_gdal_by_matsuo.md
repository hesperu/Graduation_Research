GDAL公式サイト（ラスタ）
https://gdal.org/programs/index.html#raster-programs

# GDAL は、PDS3ラスタを認識する。ただし、.lblを読ませる必要がある。
  ENVI形式は、.img を読ませなければならない。

# フォーマット変更
gdalwarp -ot Float32 <input_file>.LBL <output_file>.tif -of GTiff
形式 https://gdal.org/drivers/raster/index.html
gdal_translate 

# 地図投影法の変更
## あるファイルの投影法に合わせたい時
gdalsrsinfo -o wkt other.tif > target.wkt
gdalwarp -t_srs target.wkt source.tif output.tif

## 投影法を明に指定する時
see gdalwarp documents...

# 画像のクリップ
gdal_translate -projwin -75.3 5.5 -73.5 3.7 -of GTiff original.tif new.tif
-projwin <ulx> <uly> <lrx> <lry>

gdalwarp -te -25440.000 4080.000 4800.000 -26160.000 original.tif new.tif
<xmin ymin xmax ymax>

# ファイル間演算
gdal_calc.py -A input.tif --outfile=result.tif --calc="A*(A>0)" --NoDataValue=0
gdal_calc.py -A input.tif -B input2.tif --outfile=result.tif --calc="(A+B)/2"
gdal_calc.py --type=Float32 -A 749_MI_MAP_03_N01E000N00E001SC.tif -B 1001_MI_MAP_03_N01E000N00E001SC.tif --calc="((A*1.0)/(B*1.0))" --outfile=749_1001_MI_MAP_03_N01E000N00E001SC.tif
if the result become a integer, times 1.0 before the calculation.

# 仮想ラスタ (virtual raster, .vrt) を作る
ls *.lbl > list.txt
gdalbuildvrt -input_file_list list.txt DTM_MAP_01_N01E000S01E002SC.vrt


# 仮想ラスタの解像度を下げると同時に、フォーマットを変換する
## サイズを確認
gdalinfo DTM_MAP_01_N01E000S01E002SC.vrt
Size is 8192, 8192 と確認できた。2048x2048 に解像度を下げる

## ENVI形式に変換し、解像度を下げる。
gdalwarp -of ENVI -r average -ts 2048 2048
DTM_MAP_01_N01E000S01E002SC.vrt DTM_MAP_01_N01E000S01E002SC.img

## 地理情報のついていない形式への変換
gdal_translate -of JPEG -scale -co worldfile=yes TCO_MAPm04_N03E000N00E003SC.lbl.tif TCO_MAPm04_N03E000N00E003SC.lbl.tif.jpg
gdal_translate -of PNG -scale -co worldfile=yes TCO_MAPm04_N03E000N00E003SC.lbl.tif TCO_MAPm04_N03E000N00E003SC.lbl.tif.png

## 画像分割
gdal_retile.py -ps 5000 4000 -targetDir target source.tif

## 画像統合
gdal_merge.py -o output.tif --optfile A.tif B.tif C.tif
gdal_merge.py -o output.tif MI_MAP_03_S01E001S02E002SC.lbl MI_MAP_03_N00E001S01E002SC.lbl

-separateをつけると、元ファイルの各バンドを、統合先で別々のバンドに保存してくれる

## Gray scale image to RGB image
gdal_translate -colorinterp red,green,blue TCO_MAPm04_N00E000S03E003SC.png.tif -of GTiff out_.tif

3色だけでなく多バンドにできる。<red|green|blue|alpha|gray|undefined[,red|green|blue|alpha|gray|undefined]*>

## Convert Tiff to GTiff 
gdal_translate -of GTiff -a_srs <.wkt> -a_ullr -7.403 7.403 90962.648 -90962.648 <input.tif> <output.tif>

Prepare a image with geoinfo whose location and range are same. Make wkt file from the image. then execute above

## Extract a band image
gdal_translate -b 1 MI_MAP_03_N01E000N00E001SC.lbl 414_MI_MAP_03_N01E000N00E001SC.tif -of GTiff

# Tips: How to deal with geo coded data in python
https://gis.stackexchange.com/questions/243639/how-to-take-cell-size-from-raster-using-python-or-gdal-or-rasterio/243648#243648

# Rasterize geocoded shape file
gdal_rasterize -burn 1 -of GTiff -tr 7.403 7.403 <InputFile>.shp <OutFile>.tif

# 下絵のProjectionをwktで出力して適用。その際に画像のサイズを下絵に揃えるために-teオプションを利用
gdalwarp -t_srs target.wkt -te  -7.403 -90962.648 90962.648 7.403 N0E0_rayed_reverse_faults_test.tif N0E0_rayed_reverse_faults_test_wkt_ext.tif

# memo
地理情報がついていないHparameterデータに、Divinerデータから抽出した｀wkt｀ファイルをあてがって、地図投影する。画像の左上、右下のMapx Mapyの値を計算していれる（解像度✕ピクセル数） 
 2003  gdal_translate -of GTiff -a_srs dgdr_tb7_avg_cyl_20100303n_128_img.wkt -a_ullr -5458203.072 2122634.528 5458203.072 -2122634.528 hpar_global128ppd_v1c.tif hpar_global128ppd_v1c_gtiff.tif
かぐやデータと同じ投影法にする（解像度を7.403ｍに擬似的にしていることに注意）
 2004  gdalwarp -t_srs target.wkt hpar_global128ppd_v1c_gtiff.tif output.tif
No Data Valueの値をｰ32768にする
 2005  gdal_calc.py -A output.tif --outfile=result.tif --calc="A" --NoDataValue=-3276
