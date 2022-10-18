# データ関連

## 使うデータ
- SLDEM2013
- LRO NAC DTM
- LRO NAC

## データの取り扱い方

### PDS3
Planetary Data System 公式ドキュメント  
<https://pds.nasa.gov/datastandards/pds3/standards/>  
特にchapter3にデータ形式のラベルの読み方が書いてある。
<https://pds.nasa.gov/datastandards/pds3/standards/sr/Chapter03.pdf>  

### PDS4
Planetary Data System 公式ドキュメント  
<https://pds.nasa.gov/datastandards/documents/>  

### スクリプトでIMGファイルを使って色々やりたい時  
- 宇宙の小箱っていうCG製作サイトのKAGUYAデータでのサンプル  
<https://www.isas.jaxa.jp/home/showcase/xR/kaguya-dem.html.ja>  

- DARTSのKAGUYAのページ  
<https://darts.isas.jaxa.jp/planet/project/selene/faq_selene.html>  

### SLDEM2013について

- Simple Cylindrical (SC)地図投影法,日本語で円筒図法というもので作られている? (これはもしかしたらオルソ画像の方かもしれない)← そんなことなかった。  MAP_PROJECTION_TYPE = "SIMPLE CYLINDRICAL"って書いてあった。lblファイルを参照
    - 高緯度になればなるほど形状がくずれちゃうよ〜〜〜！！！ 
    - 横メルカトル図法に直してから精度の検証をしている論文がある [2] Tsubouchi+(2016)  
        - でもこれはオルソ画像の検証

- 64800個のデータ [1] Onodera+(2018)

### カラーマッピング color mapping
画像の色の概念
SLDEMはviridisカラーマップがデフォ
可視画像とのペアをとる場合、greyにしないといけない
matlatb.pyplot のimsaveだとこれを引数で指定できる

### 太陽高度
- 英語ではsolar zenith angleという。
    - incident angleの方がヒットした。
    - NACの太陽高度の情報はPDSのデータリポジトリにあるのではなくLROCの画像検索サイトで見れるっぽい
        - NACのtifを見るところで、詳細が表示されるが、詳細が表示されないものもある...
        - https://wms.lroc.asu.edu/lroc/view_lroc/
- 結論
    - オルソ画像のディレクトリに書いてあるNACの製品IDを　見て、そのIDを元にデータ検索サイトに入れると太陽高度の情報が出てきまーす！
    1. まずhttps://wms.lroc.asu.edu/lroc/rdr_product_select　でNAC DTMを調べると、その場所のいオルソ画像も一緒に出てくる
    2. 調べて出てきたDTMのページからPDSのページに飛ぶ。するとIMG形式でDTMに関連したデータshaded reliefとかオルソ画像とかが入っているディレクトリへといける
    3. オルソ画像はNACのID(Mで始まる数字の文字列）が入っている。それをhttps://ode.rsl.wustl.edu/moon/ 入力して元データを見つけてくる。
    4. 元データのメタデータにincident angleが記載されている。

- LRO NACのデータに記載されているか？

## 参考文献
[1] Onodera+(2020) “Resolution enhancement of DEM of the lunar surface using machine learning”.
http://doi.org/10.20637/JAXA-RR-19-006/0003

[2] Tsubouchi+(2016) "SELENE(かぐや)搭載地形カメラステレオペアデータから得られた数値地形モデル（DTM）ならびに数値標高モデル（DEM）プロダクトの標高値の検証報告"
https://jaxa.repo.nii.ac.jp/?action=pages_view_main&active_action=repository_view_main_item_detail&item_id=2462&item_no=1&page_id=13&block_id=21
