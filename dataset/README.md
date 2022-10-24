# 元データのダウンロード方法

## SLDEM2015
```sh
wget --continue -r -l 1 -A IMG,LBL -w 5 -nd http://imbrium.mit.edu/DATA/SLDEM2015/TILES/FLOAT_IMG/
```

# データセットの作り方
1. LRO NAC Orthoのincident angleを確認して条件を満たすようなデータを取ってくる。(スクレイピング？）
2. SLDEM2015の全データを取ってくる。IMGファイルなので、gdal_translateを使ってgeotiffに直しておく
3. とってきたLRO NAC Orthoそれぞれの画像範囲に重なるようなSLDEM2015を見つける。その後は、まずLRO NAC Orthoの分解能をSLDEMと同じになるようにダウンサンプリングする。同じになった画像ら、256x256ピクセルでNAC,SLDEMを切り出していく。切り出したものを一枚に並べて、256x512ピクセルの画像にする。これでデータセットの完成。

## Geotiffがpix2pixで使えるのかどうか？
なんか普通の画像ビューアーで見れないならできない気もするけど、やってるっぽい記事がある

## GdalでGeotiff→pngだとうまくいかない
