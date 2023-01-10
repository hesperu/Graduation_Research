import argparse
import pathlib
import torch
import torchvision.transforms as transforms
import torchvision.utils as utils
import numpy as np
from generator import Generator
from PIL import Image
from torch.autograd import Variable
import validate
import json



class TestDataset(torch.utils.data.Dataset):
    def __init__(self,path):
        self.data_path = path
        self.data_list = self._paths_sorted(list(pathlib.Path(path).glob("*.tiff")))

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
    
    def _paths_sorted(self,paths):
        """
        nacとsldemの画像をソートする
        わざわざ関数にしたのはpathlibでnatural sortが使えないから
        """
        return sorted(paths,key=lambda x:x.name)


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
parser.add_argument("--dataset",required=False,help="データセットのパス",default="../test/")
parser.add_argument("--model",required=False,type=str,default="./output/pix2pix_G_high_epoch_3000.pth",help="使うモデル")
opt = parser.parse_args()
model = Generator().to(torch.device("cuda"))
model.load_state_dict(torch.load(opt.model))
model.eval()

path_list = ["HPONDS","LICHTENBERG","APOLLO11","IMBRIUM"]

for dir_path in path_list:
    dir_path = pathlib.Path(__file__).parent.parent.joinpath("test",dir_path)
    dataset = TestDataset(dir_path)
    dataloader = torch.utils.data.DataLoader(dataset,batch_size=1,shuffle=True)
    
    cnt = 0
    for batch_num, data in enumerate(dataloader):
        data = data.to(torch.device("cuda"))
        out_img = model(data)
        utils.save_image(out_img,pathlib.Path(__file__).parent.parent.joinpath("test","test_result",dir_path.name,str(cnt).zfill(4)+".tiff"),normalize=True,range=(0.0,10000))
        tmp = out_img[0,:,:,:]
        tmp = tmp.permute(1,2,0)
        tmp = tmp.to('cpu').detach().numpy().copy()
        # img_pil = Image.fromarray((tmp*255).astype(np.uint8))
        #print(tmp*255)
        #img = out_img.to('cpu').detach().numpy().copy()[0]
        #print(img.shape)
        #img = Image.fromarray(img)
        #print(img)
        # img = transforms.functional.to_pil_image(img)
        #img.save(pathlib.Path(__file__).parent.parent.joinpath("test","test_result",dir_path.name,str(cnt).zfill(4)+".tiff"))
        #origin_img.save(str(pathlib.Path(__file__).parent.parent.joinpath("data_resource","test_result","origin_"+image_name.name)))
        #img_pil.save(pathlib.Path(__file__).parent.parent.joinpath("test","test_result",dir_path.name,str(cnt).zfill(4)+".tiff"))
        cnt += 1

    rmse_res = 0.0
    mae_res = 0.0
    rmse_arr = np.zeros(len(list(pathlib.Path(__file__).parent.parent.joinpath("test","test_result",dir_path.name).glob("*.tiff"))))
    mae_arr = np.zeros(len(list(pathlib.Path(__file__).parent.parent.joinpath("test","test_result",dir_path.name).glob("*.tiff"))))
    print(dir_path)

    #パス、RMSE,MAE,を持つ
    generated_list = []
    
    for i,img_path in enumerate(list(pathlib.Path(__file__).parent.parent.joinpath("test","test_result",dir_path.name).glob("*.tiff"))):
        generated = Image.open(img_path).convert("L")
        #print(np.asarray(generated).shape)
        real_ = Image.open(pathlib.Path(__file__).parent.parent.joinpath("test","evalution_dem",dir_path.name,"nac_dtm",img_path.name))
        cur_rmse = validate.calc_rmse(generated,real_)
        rmse_arr[i] = cur_rmse
        rmse_res += cur_rmse
        generated_list.append({"name":img_path.name,"rmse":cur_rmse,"mae":0})

    for i,img_path in enumerate(list(pathlib.Path(__file__).parent.parent.joinpath("test","test_result",dir_path.name).glob("*.tiff"))):
        generated = Image.open(img_path)
        real_ = Image.open(pathlib.Path(__file__).parent.parent.joinpath("test","evalution_dem",dir_path.name,"nac_dtm",img_path.name))
        cur_mae = validate.calc_mae(generated,real_)
        mae_arr[i] = cur_mae
        mae_res += cur_mae
        generated_list[i]["mae"] = cur_mae

    rmse_res /= len(list(pathlib.Path(__file__).parent.parent.joinpath("test","test_result",dir_path.name).glob("*.tiff")))
    mae_res /= len(list(pathlib.Path(__file__).parent.parent.joinpath("test","test_result",dir_path.name).glob("*.tiff")))
    validate.plot_hist(rmse_arr,"RMSE",pathlib.Path(__file__).parent.parent.joinpath("test","test_result",dir_path.name).joinpath("rmse_hist.png"))
    validate.plot_hist(rmse_arr,"MAE",pathlib.Path(__file__).parent.parent.joinpath("test","test_result",dir_path.name).joinpath("mae_hist.png"))

    print("rmseの結果が{rmse}で、maeの結果が{mae}".format(rmse=rmse_res,mae=mae_res))

    rmse_top100 = pathlib.Path(__file__).parent.parent.joinpath("test","test_result",dir_path.name,"rmse_top100")
    rmse_worst100 = pathlib.Path(__file__).parent.parent.joinpath("test","test_result",dir_path.name,"rmse_worst100")
    mae_top100 = pathlib.Path(__file__).parent.parent.joinpath("test","test_result",dir_path.name,"mae_top100")
    mae_worst100 = pathlib.Path(__file__).parent.parent.joinpath("test","test_result",dir_path.name,"mae_worst100")
    if rmse_top100.exists():
        pass
    else:
        rmse_top100.mkdir()
    if rmse_worst100.exists():
        pass
    else:
        rmse_worst100.mkdir()
    if mae_top100.exists():
        pass
    else:
        mae_top100.mkdir()
    if mae_worst100.exists():
        pass
    else:
        mae_worst100.mkdir()
    
    #RMSEでソート
    generated_list = sorted(generated_list,key=lambda value:value["rmse"])
    for i,generated in enumerate(generated_list):
        if i > 100:
            break
        img = Image.open(pathlib.Path(__file__).parent.parent.joinpath("test","test_result",dir_path.name,generated["name"]))
        real_ = Image.open(pathlib.Path(__file__).parent.parent.joinpath("test","evalution_dem",dir_path.name,"nac_dtm",generated["name"]))
        vis = Image.open(pathlib.Path(__file__).parent.parent.joinpath("test",dir_path,generated["name"]))
        aligned = Image.new("L",(vis.width + img.width + real_.width, img.height))
        aligned.paste(vis,(0,0))
        aligned.paste(img,(img.width,0))
        aligned.paste(real_,(vis.width+img.width,0))
        aligned.save(rmse_top100.joinpath(str(i+1).zfill(3)+".tiff"))
        json_path = rmse_top100.joinpath(str(i+1).zfill(3)+".json")
        json_file = open(str(json_path),mode="w")
        json.dump(generated,json_file)
        json_file.close()
    
    generated_list = sorted(generated_list,key=lambda value:value["rmse"],reverse=True)
    for i,generated in enumerate(generated_list):
        if i > 100:
            break
        img = Image.open(pathlib.Path(__file__).parent.parent.joinpath("test","test_result",dir_path.name,generated["name"]))
        real_ = Image.open(pathlib.Path(__file__).parent.parent.joinpath("test","evalution_dem",dir_path.name,"nac_dtm",generated["name"]))
        vis = Image.open(pathlib.Path(__file__).parent.parent.joinpath("test",dir_path,generated["name"]))
        aligned = Image.new("L",(vis.width + img.width + real_.width, img.height))
        aligned.paste(vis,(0,0))
        aligned.paste(img,(img.width,0))
        aligned.paste(real_,(vis.width+img.width,0))
        aligned.save(rmse_worst100.joinpath(str(i+1).zfill(3)+".tiff"))
        json_path = rmse_worst100.joinpath(str(i+1).zfill(3)+".json")
        json_file = open(str(json_path),mode="w")
        json.dump(generated,json_file)
        json_file.close()

    generated_list = sorted(generated_list,key=lambda value:value["mae"])
    for i,generated in enumerate(generated_list):
        if i > 100:
            break
        img = Image.open(pathlib.Path(__file__).parent.parent.joinpath("test","test_result",dir_path.name,generated["name"]))
        real_ = Image.open(pathlib.Path(__file__).parent.parent.joinpath("test","evalution_dem",dir_path.name,"nac_dtm",generated["name"]))
        vis = Image.open(pathlib.Path(__file__).parent.parent.joinpath("test",dir_path,generated["name"]))
        aligned = Image.new("L",(vis.width + img.width + real_.width, img.height))
        aligned.paste(vis,(0,0))
        aligned.paste(img,(img.width,0))
        aligned.paste(real_,(vis.width+img.width,0))
        aligned.save(mae_top100.joinpath(str(i+1).zfill(3)+".tiff"))
        json_path = mae_top100.joinpath(str(i+1).zfill(3)+".json")
        json_file = open(str(json_path),mode="w")
        generated
        json.dump(generated,json_file)
        json_file.close()

    generated_list = sorted(generated_list,key=lambda value:value["mae"],reverse=True)
    for i,generated in enumerate(generated_list):
        if i > 100:
            break
        img = Image.open(pathlib.Path(__file__).parent.parent.joinpath("test","test_result",dir_path.name,generated["name"]))
        real_ = Image.open(pathlib.Path(__file__).parent.parent.joinpath("test","evalution_dem",dir_path.name,"nac_dtm",generated["name"]))
        vis = Image.open(pathlib.Path(__file__).parent.parent.joinpath("test",dir_path,generated["name"]))
        aligned = Image.new("L",(vis.width + img.width + real_.width, img.height))
        aligned.paste(vis,(0,0))
        aligned.paste(img,(img.width,0))
        aligned.paste(real_,(vis.width+img.width,0))
        aligned.save(mae_worst100.joinpath(str(i+1).zfill(3)+".tiff"))
        json_path = mae_worst100.joinpath(str(i+1).zfill(3)+".json")
        json_file = open(str(json_path),mode="w")
        json.dump(generated,json_file)
        json_file.close()


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