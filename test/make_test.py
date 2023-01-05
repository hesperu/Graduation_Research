from PIL import Image
import pathlib

Image.MAX_IMAGE_PIXELS = 1000000000 #pillowで使えるピクセル数の上限を大きくしないとエラーが起きる

def cut():
    current_dir = pathlib.Path(__file__).parent
    cut_width = 256
    cut_height = 256
    cnt = 0
    #可視画像の分割
    """
    for tiff_path in list(current_dir.glob("*.tiff")):
        dir_path = pathlib.Path(tiff_path.stem)
        if dir_path.exists():
            pass
        else:
            dir_path.mkdir()
        print(tiff_path)
        tiff_img = Image.open(tiff_path)
        for i in range(0,tiff_img.height,cut_height):
            for j in range(0,tiff_img.width,cut_width):
                tiff_crop = tiff_img.crop((j,i,j+cut_width,i+cut_height))
                tiff_crop.save(dir_path.joinpath(str(cnt).zfill(3)+".tiff"))
                cnt += 1
    """
    cnt = 0
    #sldemの分割
    dem_dir_path = current_dir.joinpath("evalution_dem")
    """
    for tiff_path in list(current_dir.glob("*.tiff")):
        dir_path = dem_dir_path.joinpath(tiff_path.stem)
        sldem_dir_path = dir_path.joinpath("sldem")
        if sldem_dir_path.exists():
            pass
        else:
            sldem_dir_path.mkdir()
        
        sldem_img = Image.open(str(dem_dir_path.joinpath("sldem_"+tiff_path.name)))
        for i in range(0,sldem_img.height,cut_height):
            for j in range(0,sldem_img.height,cut_width):
                sldem_crop = sldem_img.crop((j,i,j+cut_width,i+cut_height))
                sldem_crop.save(sldem_dir_path.joinpath(str(cnt).zfill(3)+".tiff"))
                cnt += 1
    """

    cnt = 0
    for tiff_path in list(current_dir.glob("*.tiff")):
        dir_path = dem_dir_path.joinpath(tiff_path.stem)
        if dir_path.exists():
            pass
        else:
            dir_path.mkdir()

        nac_dtm_dir_path = dir_path.joinpath("nac_dtm")
        if nac_dtm_dir_path.exists():
            pass
        else:
            nac_dtm_dir_path.mkdir()
        
        nac_dtm_img = Image.open(str(dem_dir_path.joinpath("nac_dtm_"+tiff_path.name)))
        for i in range(0,nac_dtm_img.height,cut_height):
            for j in range(0,nac_dtm_img.width,cut_width):
                nac_dtm_crop = nac_dtm_img.crop((j,i,j+cut_width,i+cut_height))
                nac_dtm_crop.save(nac_dtm_dir_path.joinpath(str(cnt).zfill(3)+".tiff"))
                cnt += 1

def remove_disused():
    """
    cutをやると黒い隙間がある画像が生成されるときがある。
    可視画像の方でそれを目視で削除する。
    """
    current_dir = pathlib.Path(__file__).parent
    dem_dir_path = current_dir.joinpath("evalution_dem")

    for tiff_path in list(current_dir.glob("*.tiff")):
        dir_path = dem_dir_path.joinpath(tiff_path.stem)
        nac_dtm_dir_path = dir_path.joinpath("nac_dtm")
        
        for dtm_img_path in list(nac_dtm_dir_path.glob("*.tiff")):
            flag = False
            nac_dir = current_dir.joinpath((tiff_path.stem))
            for nac in list(nac_dir.glob("*.tiff")):
                if nac.name == dtm_img_path.name:
                    flag = True
            if not flag:
                dtm_img_path.unlink(missing_ok=False)
            else:
                print("{p}削除しませーん".format(p=dtm_img_path))

"""生成画像と本物を比較するときのために"""
def rename():
    current_dir = pathlib.Path(__file__).parent
    dem_dir_path = current_dir.joinpath("evalution_dem")

    for tiff_path in paths_sorted(list(current_dir.glob("*.tiff"))):
        dir_path = dem_dir_path.joinpath(tiff_path.stem)
        nac_dtm_dir_path = dir_path.joinpath("nac_dtm")
        cnt = 0
        for dtm_img_path in paths_sorted(list(nac_dtm_dir_path.glob("*.tiff"))):
            img = Image.open(str(dtm_img_path))
            img.save(str(dtm_img_path.parent.joinpath(str(cnt).zfill(4)+".tiff")))
            cnt += 1

def paths_sorted(paths):
    """
    nacとsldemの画像をソートする
    わざわざ関数にしたのはpathlibでnatural sortが使えないから
    """
    return sorted(paths,key=lambda x:x.name)


if __name__ == "__main__":
    cut()
    # remove_disused()
    # rename()