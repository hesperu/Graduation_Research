import argparse
import pathlib
import torch
import torchvision.transform 
import numpy as np
from PIL import Image
from torch.autograd import Variable


def load_img(path):
    img = Image.open(path)
    return img

def save_img(image_tensor,path):
    image_numpy = image_tensor.float().numpy()
    image_numpy = (np.transpose(image_numpy, (1, 2, 0)) + 1) / 2.0 * 255.0
    image_numpy = image_numpy.astype(np.uint8)
    image_pil = Image.fromarray(image_numpy)
    image_pil.save(path)
    print( "Image saved as {}".format(path))

parser = argparse.ArgumentParser("pix2pix")
parser.add_argument("--dataset",required=True,help="データセットのパス")
parser.add_argument("--model",type=str,default="./output/pix2pix_D_epoch_10000",help="使うモデル")
opt = parser.parse_args()

netG = torch.load(opt.model)
image_dir = opt.dataset
image_filenamaes = [x for x in list(pathlib.Path(image_dir).glob("*./tiff"))]
transform_list = [transforms.ToTensor(),
                  transforms.Normalize((0.5, 0.5, 0.5), (0.5, 0.5, 0.5))]

transform = transforms.Compose(transform_list)

for image_name in image_filenames:
    img = load_img(image_dir + image_name)
    img = transform(img)
    input = Variable(img, volatile=True).view(1, -1, 256, 256)

    out = netG(input)
    out = out.cpu()
    out_img = out.data[0]
    if pathlib.Path(__file__).parent.joinpath("test_result").exists():
        pass
    else:
        pathlib.Path(__file__).parent.joinpath("test_result").mkdir()
    save_img(out_img,"result/"+"image_name"+".tiff")