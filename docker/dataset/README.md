# データセット作成のためのDocker環境

## なぜ必要？
GDALの依存関係が複雑。Pythonの環境と、シェルに入れておくGDALの環境がぐちゃぐちゃに絡まっていてうまくビルドできないから

### ビルド方法
ここに書いてあるimageをpullする
https://github.com/andriyreznik/docker-python-gdal

Dockerfileをそのままビルドしたら永遠に終わらなかった
コンテナ作ったあとにrequirements.txtで各種パッケージをインストールするのがいいかもね