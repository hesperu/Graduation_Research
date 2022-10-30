# 元データのダウンロード方法

## SLDEM2015
```sh
wget --continue -r -l 1 -A IMG,LBL -w 5 -nd http://imbrium.mit.edu/DATA/SLDEM2015/TILES/FLOAT_IMG/
```
## SLDEM
```sh
wget --continue -r -l 1 -A img,lbl -w 5 -nd https://data.darts.isas.jaxa.jp/pub/pds3/sln-l-tc-5-sldem2013-v1.0/lon***/data/
```

# データセットの作り方
1. LRO NAC Orthoのincident angleを確認して条件を満たすようなデータを取ってくる。(スクレイピング？）
2. SLDEM2015の全データを取ってくる。IMGファイルなので、gdal_translateを使ってgeotiffに直しておく
3. とってきたLRO NAC Orthoそれぞれの画像範囲に重なるようなSLDEM2015を見つける。その後は、まずLRO NAC Orthoの分解能をSLDEMと同じになるようにダウンサンプリングする。同じになった画像ら、256x256ピクセルでNAC,SLDEMを切り出していく。切り出したものを一枚に並べて、256x512ピクセルの画像にする。これでデータセットの完成。

## Geotiffがpix2pixで使えるのかどうか？
なんか普通の画像ビューアーで見れないならできない気もするけど、やってるっぽい記事がある

## GdalでGeotiff→pngだとうまくいかない
解決。
```sh
gdal_translate -of PNG -ot Byte -scale in_tiff.tif out_png_scaled.png
```
-ot をUInt,IntではなくByteにしないと真っ黒の画像が生成されてしまう。 

### なんで？
- gdal_translate だけでは数値型を上手く扱えないから
- gdal_translateの-otでバンドの画像の数値型を指定してあげないといけない。
 - gdalinfoで得られるBandの所に書いてある型を指定する

## gdalで分解能を落とす
gdalwarpを使う  
https://gdal.org/programs/gdalwarp.html#cmdoption-gdalwarp-r
```sh
gdalwarp -tr 100 100  -r high.tiff low.tiff
```
これは分解能を100に落としている例
ちなみに画像が大きすぎると無限時間かかるのでやめといた方が良い。  
LRO NAC の元画像だとすぐにできるけど。
