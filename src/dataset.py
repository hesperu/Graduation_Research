import torch
import torchvision
import pathlib
import sys
from PIL import Image

class AlignedDataset(torch.utils.data.Dataset):
    """
    同じ場所のSLDEMとNACのペア画像を作る
    ただ並べるだけで、元の画像の処理方法はめんどいのでdatasetに置いてある
    """

    IMAGE_EXTENSIONS = ["png","png"]

    def __init__(self,config):
        """
        configはパラメータ設定
        parameter.pyに定義している
        """
        self.config = config
        dir = pathlib.Path(config.dataroot)
    
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

        for file_name in list(nac_dir.glob("/*" + self.IMAGE_EXTENSIONS[0])):
            nac_images.append(file_name)
        
        for file_name in list(sldem_dir.glob("/*" + self.IMAGE_EXTENSIONS[1])):
            sldem_images.append(file_name)

        if len(nac_images) != len(sldem_images):
            print("データセットの数がNACとSLDEMで違うよ! 確認してね")
            sys.exit(1)
        
        nac_images = self._paths_sorted(nac_images)
        sldem_images = self._paths_sorted(sldem_images)
        dataset_dir = self._align_dataset(dir,nac_images,sldem_images)

        return dataset_dir

    def _paths_sorted(self,paths):
        """
        nacとsldemの画像をソートする
        わざわざ関数にしたのはpathlibでnatural sortが使えないから
        """
        return sorted(paths,key=lambda x: int(x.name))
    
    def _align_dataset(self,dir,nac_dir,sldem_dir):
        save_dir = dir.joinpath(self.IMAGE_EXTENSIONS[0] + "_dataset")
        
        if save_dir.exists():
            pass
        else:
            save_dir.mkdir()

        for i,nac_path,sldem_path in enumerate(zip(nac_dir,sldem_dir)):
            nac_img = Image.open(str(nac_path))
            nac_img = nac_img.convert("L")
            sldem_img = Image.open(str(sldem_path))
            sldem_img = sldem_img.convert("L")

            aligned_image = Image.new("GRAY",(nac_img.width + sldem_img.width, nac_img.height))
            aligned_image.paste(nac_img,(0,0))
            aligned_image.paste(sldem_img,(nac_img.width,0))
            aligned_image.save(str(save_dir.joinpath(str(i).zfill(5))))
        
        return save_dir