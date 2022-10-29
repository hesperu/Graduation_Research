# 壊れているから使えない
for i in {0..359}
do
    NAME = $(printf "%lon03d" $i)
    mkdir $NAME
done