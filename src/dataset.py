import torch
import torchvision
import pathlib
import sys
import numpy as np
import random
from PIL import Image

class AlignedDataset(torch.utils.data.Dataset):
    """
    同じ場所のSLDEMとNACのペア画像を作る
    ただ並べるだけで、元の画像の処理方法はめんどいのでdatasetに置いてある
    """

    IMAGE_EXTENSIONS = ["tiff","tiff"]

    def __init__(self,config):
        """
        configはパラメータ設定
        parameter.pyに定義している
        """
        self.config = config
        dir = pathlib.Path(config.dataroot)
        self.dataset_list = self._make_dataset(dir)
        self.dataset_len = len(self.dataset_list)

    def _make_dataset(self,dir):
        """
        データセットディレクトリを引数にする
        parameterで定義したdirは
        /ssd4T/ibuka_dataset/pix2pix_training
        この配下に学習用のデータセットを置いておく
        """
        nac_images = []
        sldem_images = []

        if dir.exists():
            pass
        else:
            print("ディレクトリ指定間違ってない？ {dir}は存在しないよ！".format(str(dir)))
            sys.exit(1)
        
        """
        pngとtiffの二種類を用意
        IMAGE_EXTENSIONSで指定できるようにしておく
        """
        nac_dir = dir.joinpath("nac",self.IMAGE_EXTENSIONS[0])
        sldem_dir = dir.joinpath("sldem",self.IMAGE_EXTENSIONS[1])

        if nac_dir.exists():
            pass
        else:
            nac_dir.mkdir()

        if sldem_dir.exists():
            pass
        else:
            sldem_dir.mkdir()

        for file_name in list(nac_dir.glob("*." + self.IMAGE_EXTENSIONS[0])):
            nac_images.append(file_name)
        
        for file_name in list(sldem_dir.glob("*." + self.IMAGE_EXTENSIONS[1])):
            sldem_images.append(file_name)

        if len(nac_images) != len(sldem_images):
            print("データセットの数がNACとSLDEMで違うよ! 確認してね")
            sys.exit(1)
        
        nac_images = self._paths_sorted(nac_images)
        sldem_images = self._paths_sorted(sldem_images)
        dataset_list = self._align_dataset(dir,nac_images,sldem_images)

        return dataset_list

    def _paths_sorted(self,paths):
        """
        nacとsldemの画像をソートする
        わざわざ関数にしたのはpathlibでnatural sortが使えないから
        """
        return sorted(paths,key=lambda x:x.name)
    
    def _align_dataset(self,dir,nac_dir,sldem_dir):
        save_dir = dir.joinpath(self.IMAGE_EXTENSIONS[0] + "_dataset")
        image_list = []

        if save_dir.exists():
            pass
        else:
            save_dir.mkdir()

        for i,(nac_path,sldem_path) in enumerate(zip(nac_dir,sldem_dir)):
            nac_img = Image.open(str(nac_path))
            nac_img = nac_img.convert("L")
            sldem_img = Image.open(str(sldem_path))
            sldem_img = sldem_img.convert("L")
            
            for j in range(self.config.augmentation_interval):
                # クロップ位置を乱数で決定
                i, j, h, w = torchvision.transforms.RandomCrop.get_params(nac_img,output_size=(self.config.crop_size,self.config.crop_size))
                crop_nac = torchvision.transforms.functional.crop(nac_img,i,j,h,w)
                crop_sldem = torchvision.transforms.functional.crop(sldem_img,i,j,h,w)
                
                h_rand = random.random()
                v_rand = random.random()
                if h_rand > 0.5:
                    h_rand = 1
                else:
                    h_rand = 0
                if v_rand > 0.5:
                    v_rand = 1
                else: v_rand = 0

                h_transform = torchvision.transforms.RandomHorizontalFlip(h_rand)
                v_transform = torchvision.transforms.RandomVerticalFlip(v_rand)
                crop_nac = h_transform(crop_nac)
                crop_nac = v_transform(crop_nac)
                crop_sldem = h_transform(crop_sldem)
                crop_sldem = v_transform(crop_sldem)

                aligned_image = Image.new("L",(crop_nac.width + crop_sldem.width, crop_nac.height))
                aligned_image.paste(crop_nac,(0,0))
                aligned_image.paste(crop_sldem,(crop_nac.width,0))
                aligned_image.save(str(save_dir.joinpath(nac_path.name+str(i).zfill(5))) + "."+ str(self.IMAGE_EXTENSIONS[0]))
                image_list.append((str(save_dir.joinpath(nac_path.name+str(i).zfill(5))) + "."+ str(self.IMAGE_EXTENSIONS[0])))

        return image_list
    
    def _transform(self):
        list = []
        
        list += [
            torchvision.transforms.ToTensor(),
            torchvision.transforms.Normalize((0.5, 0.5, 0.5), (0.5, 0.5, 0.5))
        ]
        
        return torchvision.transforms.Compose(list)    

    def __len__(self):
        return self.dataset_len

    def __getitem__(self,index):
        #統合した画像から分割して画像を会得する
        AB_path = self.dataset_list[index]
        AB = Image.open(AB_path).convert("RGB")
        w,h = AB.size
        half_w = int(w/2)
        
        transform = self._transform()
        #ここからそれぞれ画像生成
        A = transform(AB.crop((0,0,half_w,h)))
        B = transform(AB.crop((half_w,0,w,h)))

        return {'A':A, 'B':B, 'A_paths':AB_path, 'B_paths':AB_path}
