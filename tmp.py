import numpy as np
import matplotlib.pyplot as plt
import tifffile

# lblファイルの下記の記述を参照
#   SAMPLE_TYPE = PC_REAL  ... 4-, 8-, and 10-byte real number
#   SAMPLE_BITS = 16           ... 1画素あたり16bits
data = np.fromfile('./dataset/origin/sldem/SLDEM2015_256_0N_60N_000_120_FLOAT.IMG', dtype='f4')

# lblファイルの以下の記述より配列の形を変更
#   LINES = 15360
#   LINE_SAMPLES = 30720
LINES = 15360
LINE_SAMPLES = 30720
image = data.reshape(LINES,LINE_SAMPLES)

image = image[0:100,0:100]
# lblファイルの以下の記述より、データ加工なしにそのまま使う
#   OFFSET = 0.000000
#   SCALING_FACTOR = 1.000000

# データを表示(最初のバンドを表示)
tifffile.imwrite('tmp.tif',image)