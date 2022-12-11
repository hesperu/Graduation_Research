from PIL import Image
import argparse
import pathlib
Image.MAX_IMAGE_PIXELS = 1000000000

parser = argparse.ArgumentParser("input_image")
parser.add_argument("--dataset",required=True,help="カットする画像が入ってるディレクトリ")
opt = parser.parse_args()

for path in list(pathlib.Path(opt.dataset).glob("*.tiff")):
    img = Image.open(path)
    cut_width = 256
    cut_height = 256
    save_dir = pathlib.Path(__file__).parent.parent.joinpath("data_resource","test",path.stem)
    if not save_dir.exists():
        save_dir.mkdir()
    cnt = 0

    for i in range(0,img.height,cut_height):
        for j in range(0,img.width,cut_width):
            if j+cut_width < img.width and i+cut_height < img.height:
                img_crop = img.crop((j,i,j+cut_width,i+cut_height))
                img_crop.save(str(save_dir.joinpath(str(cnt).zfill(3)+".tiff")))
                cnt += 1