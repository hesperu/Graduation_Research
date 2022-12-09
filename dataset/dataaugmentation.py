from keras.preprocessing import image
from PIL import Image
import numpy as np
import sys
import pathlib
import cv2



def data_augmentation(path,sldem_type,nac_type,suffix):
    """
    画像の水増し
    対象とするのはsldem2015を使う場合だけ
    !!!
    tiff画像はkerasのデータオーギュメンテーションに使えないって！
    !!!
    """
    if sldem_type == "sldem2013":
        return

    datagen = image.ImageDataGenerator(
        rotation_range = 30,
        width_shift_range = 30,
        height_shift_range = 30,
        horizontal_flip = True,
        vertical_flip = True,
        fill_mode='constant'
    )

    training_sldem_path = pathlib.Path(path).joinpath("pix2pix_training",sldem_type)
    training_nac_path = pathlib.Path(path).joinpath("pix2pix_training",nac_type)
    DATA_GEN_COUNT = 10
    j = 0
    for nac in list(pathlib.Path(path).joinpath("processed",nac_type,"cut",suffix).glob(str("*."+suffix))):
        nac_array = cv2.imread(str(nac))
        nac_array = np.array(nac_array)
        # flowは四つの引数、n_samples,x,y,channelsを必要とする
        #そのままだとn_samplesがないので加える
        nac_array = nac_array.reshape((1,) + nac_array.shape)
        sldem_array = cv2.imread(str(pathlib.Path(path).joinpath("processed",sldem_type,"cut",suffix,nac.name)))
        sldem_array = np.array(sldem_array)
        sldem_array = sldem_array.reshape((1,) + sldem_array.shape)
        nac_save_dir = str(pathlib.Path(path).joinpath("processed",nac_type,"cut","augmented",suffix))
        sldem_save_dir = str(pathlib.Path(path).joinpath("processed",sldem_type,"cut","augmented",suffix))
        
        print(nac_array.shape)
        i = 0    
        for batch in datagen.flow(nac_array,batch_size=1,seed=1,save_to_dir=nac_save_dir,save_prefix='generated_'+str(j),save_format=suffix):
            #注意、pngかjpgの拡張子しか使えない
            i += 1
            if i == 10:
                break
        
        i = 0
        for batch in datagen.flow(sldem_array,batch_size=1,seed=1,save_to_dir=sldem_save_dir,save_prefix='generated_'+str(j),save_format=suffix):
            i += 1
            if i == 10:
                break
        j += 1

    i = 0
    for nac in list(pathlib.Path(path).joinpath("processed",nac_type,"cut","augmented",suffix).glob(str("*."+suffix))):
        print(nac)
        nac_img = Image.open(nac)
        sldem_img = Image.open(pathlib.Path(path).joinpath("processed",sldem_type,"cut","augmented",suffix).joinpath(nac.name))
        img_width,img_height = nac_img.size
        crop_width = 256
        crop_height = 256
        nac_crop = nac_img.crop(((img_width - crop_width) // 2,
                    (img_height - crop_height) // 2,
                    (img_width + crop_width) // 2,
                    (img_height + crop_height) // 2))
        sldem_crop = sldem_img.crop(((img_width - crop_width) // 2,
                    (img_height - crop_height) // 2,
                    (img_width + crop_width) // 2,
                    (img_height + crop_height) // 2))
        nac_crop.save(str(training_nac_path.joinpath(suffix,str(i)+"."+suffix)))
        sldem_crop.save(str(training_sldem_path.joinpath(suffix,str(i)+"."+suffix)))
        i += 1


if __name__ == "__main__":
    if (len(sys.argv) < 4):
        print("引数が足りないよ")
    else:
        data_augmentation(sys.argv[1],sys.argv[2],sys.argv[3],sys.argv[4])