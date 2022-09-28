<< COMMENTOUT
こ　れ　な　に　笑 ？
isisをdockerで動かす時に、CMDで使う
condaでisis環境を作るもの。
RUNだと作れないからCMDで作ろうとしたら、複数行はCMDで出来ないみたい。
COMMENTOUT
#!/bin/bash

conda install -c usgs-astrogeology isis
apt-get update
apt-get install libgl1 -y 
rm -rf /var/lib/apt/lists/
bash -lc 'python "$CONDA_PREFIX/scripts/isisVarInit.py"'
