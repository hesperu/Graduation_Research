from PIL import Image
import matlab.engine
import sys
import pathlib

Image.MAX_IMAGE_PIXELS = 1000000000 #pillowで使えるピクセル数の上限を大きくしないとエラーが起きる

def cut_by_mutualinfo(dataset_dir,sldem_type,nac_type):
        
    result_sldem_path = pathlib.Path(__file__).parent.joinpath("processed",sldem_type)
    result_nac_path = pathlib.Path(__file__).parent.joinpath("processed",nac_type)
    result_cut_sldem_tiff_path = result_sldem_path.joinpath("cut","tiff")
    result_cut_nac_tiff_path = result_nac_path.joinpath("cut","tiff")
    hillshade_dir = result_sldem_path.joinpath("hillshade")
    if hillshade_dir.exists():
        pass
    else:
        print("hillshadeのディレクトリが存在しないよ!")
        return
    cut_hillshade_dir = hillshade_dir.joinpath("cut")
    if cut_hillshade_dir.exists():
        pass
    else:
        cut_hillshade_dir.mkdir()

    import matlab.engine
    eng = matlab.engine.start_matlab()
    eng.cd("/Users/koichiro/University/research/Graduation_Research/dataset")
    """
    alignment.mを使って位置合わせする
    引数は,可視画像のパス、DTMのパス、hillshadeのパス、保存するパス
    """
    if nac_type == "nac_mosaic":
        sldem_list = list(result_sldem_path.glob("./NAC*.tiff"))
        print(sldem_list)
        for sldem in sldem_list:
            sldem_img = Image.open(sldem)
            nac_img = Image.open(result_nac_path.joinpath(sldem.name))
            hillshade_img = Image.open(hillshade_dir.joinpath(sldem.name))
            cut_width = 320
            cut_height = 320
            #切り出しスタート位置の係数。例えばper=0.1だと画像の10%のところからスタート
            height_per = 0.1
            width_per = 0.1
            #位置合わせのためにどれくらい広くピクセルをとるか
            height_expand = 20
            width_expand = 20
            cnt = 0

            for i in range(int(sldem_img.height*height_per),sldem_img.height,cut_height):
                for j in range(int(sldem_img.width*width_per),sldem_img.width,cut_width):
                    sldem_crop = sldem_img.crop((max(j-width_expand,0),max(i-height_expand,0),min(j+cut_width+width_expand,sldem_img.width),min(i+cut_height+height_expand,sldem_img.height)))
                    nac_crop = nac_img.crop((j,i,j+cut_width,i+cut_height)) # nacは広い範囲に取る
                    hillshade_crop = hillshade_img.crop(((max(j-width_expand,0),max(i-height_expand,0),min(j+cut_width+width_expand,sldem_img.width),min(i+cut_height+height_expand,sldem_img.height)))) # hillshadeは広い範囲でとる
                    save_name = sldem.stem+str(cnt).zfill(3)+sldem.suffix
                    sldem_crop.save(result_cut_sldem_tiff_path.joinpath(save_name))
                    nac_crop.save(result_cut_nac_tiff_path.joinpath(save_name))
                    hillshade_crop.save(cut_hillshade_dir.joinpath(save_name))
                    res = eng.alignment(str(result_cut_nac_tiff_path.joinpath(save_name)),str(result_cut_sldem_tiff_path.joinpath(save_name)),\
                        str(cut_hillshade_dir.joinpath(save_name)),str(result_cut_nac_tiff_path.joinpath(save_name[:-4]+"_after.tiff")))
                    cnt += 1
                    print(res)
        
    else:
        dir_list = list(result_nac_path.glob("**/*"))
        for nac_dir in dir_list:
            for nac in list(nac_dir.glob("**/*.tiff")):
                nac_img = Image.open(nac)
                sldem_img = Image.open(result_sldem_path.joinpath(nac.name))
                cut_width = 320
                cut_height = 320
                #切り出しスタート位置の係数。例えばper=0.1だと画像の10%のところからスタート
                height_per = 0.0
                width_per = 0.0
                cnt = 0

                for i in range(int(nac_img.height*height_per),nac_img.height,cut_height):
                    for j in range(int(nac_img.width*width_per),nac_img.width,cut_width):
                        sldem_crop = sldem_img.crop((j,i,j+cut_width,i+cut_height))
                        nac_crop = nac_img.crop((j,i,j+cut_width,i+cut_height))
                        sldem_crop.save(result_cut_sldem_tiff_path.joinpath(nac.stem+str(cnt).zfill(3)+nac.suffix))
                        nac_crop.save(result_cut_nac_tiff_path.joinpath(nac.stem+str(cnt).zfill(3)+nac.suffix))
                        cnt += 1

if __name__ == "__main__":
    if len(sys.argv) < 4:
        print("データセットの指定が足りないよ！")
    else:
        cut_by_mutualinfo(sys.argv[1],sys.argv[2],sys.argv[3]) # 指定するのはデータセット、sldemの種類,nacの種類