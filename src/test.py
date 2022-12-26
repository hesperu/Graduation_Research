import argparse
import pathlib
import torch
import torchvision.transforms as transforms
import torchvision.utils as utils
import numpy as np
from generator import Generator
from PIL import Image
from torch.autograd import Variable

class TestDataset(torch.utils.data.Dataset):
    def __init__(self,path):
        self.data_path = path
        self.data_list = list(pathlib.Path(path).glob("*.tiff"))

    def __len__(self):
        return len(self.data_list)
    
    def _transform(self):
        transform_list = [transforms.ToTensor(),
                transforms.Normalize((0.5,0.5,0.5),(0.5,0.5,0.5))]
        transform = transforms.Compose(transform_list)

        return transform

    def __getitem__(self,index):
        img_path = self.data_list[index]
        img = Image.open(img_path).convert("RGB")
        transform =  self._transform()
        img = transform(img)

        return img

def tensor2im(input_image, imtype=np.uint8):
    """"Converts a Tensor array into a numpy image array.
    Parameters:
        input_image (tensor) --  the input image tensor array
        imtype (type)        --  the desired type of the converted numpy array
    pix2pixの公式からとってきた
    """
    if not isinstance(input_image, np.ndarray):
        if isinstance(input_image, torch.Tensor):  # get the data from a variable
            image_tensor = input_image.data
        else:
            return input_image
        image_numpy = image_tensor[0].cpu().float().numpy()  # convert it into a numpy array
        if image_numpy.shape[0] == 1:  # grayscale to RGB
            image_numpy = np.tile(image_numpy, (3, 1, 1))
        image_numpy = (np.transpose(image_numpy, (1, 2, 0)) + 1) / 2.0 * 255.0  # post-processing: tranpose and scaling
    else:  # if it is a numpy array, do nothing
        image_numpy = input_image

    return image_numpy.astype(imtype)


def load_img(path):
    img = Image.open(path).convert("RGB")
    return img

def save_img(image_tensor,path):
    #image_numpy = image_tensor.float().detach().cpu().numpy()
    #image_numpy = (np.transpose(image_numpy, (1, 2, 0)) + 1)#/ 2.0 * 255.0
    #image_numpy = image_numpy.astype(np.uint8)
    #image_pil = Image.fromarray((image_numpy*255).astype(np.uint8))
    #image_pil.save(path)
    image_numpy = tensor2im(image_tensor)
    img = Image.fromarray(image_numpy)
    img.save(path)
    #utils.save_image(image_tensor,path,normalize=True)
    print( "Image saved as {}".format(path))

"""
保存したモデルを読み込むと出力される画像がおかしくなる
なので、現状学習した後にそのままテストするようにしてる
"""
parser = argparse.ArgumentParser("pix2pix")
parser.add_argument("--dataset",required=True,help="データセットのパス")
parser.add_argument("--model",required=False,type=str,default="./output/pix2pix_G_high_epoch_100.pth",help="使うモデル")
opt = parser.parse_args()
model = Generator().to(torch.device("cuda"))
model.load_state_dict(torch.load(opt.model))
model.eval()


dataset = TestDataset(opt.dataset)
dataloader = torch.utils.data.DataLoader(dataset,batch_size=1,shuffle=True)
cnt = 0

for batch_num, data in enumerate(dataloader):
    data = data.to(torch.device("cuda"))
    out_img = model(data)
    utils.save_image(out_img,pathlib.Path(__file__).parent.parent.joinpath("data_resource","test_result",str(cnt)+".tiff"),normalize=True)
    #origin_img.save(str(pathlib.Path(__file__).parent.parent.joinpath("data_resource","test_result","origin_"+image_name.name)))
    cnt += 1

"""
image_dir = opt.dataset
image_filenames = [x for x in list(pathlib.Path(image_dir).glob("*.tiff"))]
transform_list = [transforms.ToTensor(),
                  transforms.Normalize((0.5,0.5,0.5),(0.5,0.5,0.5))]

transform = transforms.Compose(transform_list)

for image_name in image_filenames:
    img = load_img(image_name)
    img = transform(img)#.unsqueeze(dim=0)
    input = img.to(torch.device("cuda"))
    #utils.save_image(input,pathlib.Path(__file__).parent.parent.joinpath("data_resource","test_result",image_name.name),normalize=True)
    out_img = model(input)
    if pathlib.Path(__file__).parent.parent.joinpath("data_resource","test_result").exists():
        pass
    else:
        pathlib.Path(__file__).parent.parent.joinpath("data_resource","test_result").mkdir()
    #save_img(out_img,str(pathlib.Path(__file__).parent.parent.joinpath("data_resource","test_result",image_name.name)))
    #origin_img = Image.open(image_name)
    utils.save_image(out_img,pathlib.Path(__file__).parent.parent.joinpath("data_resource","test_result",image_name.name),normalize=True)
    #origin_img.save(str(pathlib.Path(__file__).parent.parent.joinpath("data_resource","test_result","origin_"+image_name.name)))
"""