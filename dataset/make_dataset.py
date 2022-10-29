from operator import le
import pathlib
import sys
from unittest import result
import gdal
import subprocess

class DatasetProcess:
    def __init__(self,path):
        self.origin_data_path = path
        self.processed_path = self.origin_data_path.parent.joinpath("processed")
        self.dataset_path = self.origin_data_path.parent.joinpath("dataset")
        self.result_sldem_path = self.processed_path.joinpath("sldem")
        self.result_lro_nac_path = self.processed_path.joinpath("lro_nac")
        self.result_lro_nac_png_path = self.result_lro_nac_path.joinpath("png")
        self.result_cut_lro_nac_path = self.result_lro_nac_path.joinpath("cut")
        self.result_lro_nac_tiff_path = self.result_lro_nac_path.joinpath("tiff")
        self.sldem_list =list(self.origin_data_path.joinpath("sldem").glob("**/*.LBL"))
        self.nac_list = list(self.origin_data_path.joinpath("lro_nac").glob("**/*.tiff"))
        # 加工したデータセットのディレクトリが存在しないなら作る
        if self.processed_path.exists():
            pass
        else:
            self.processed_path.mkdir()
    
    def sldem2geotiff(self):
        # "加工後のsldemを保存するディレクトリがないなら作る"
        if self.result_sldem_path.exists():
            pass
        else:
            self.result_sldem_path.mkdir()
        
        for sldem in self.sldem_list:
            sldem_file_name = pathlib.Path(sldem).with_suffix(".tif").name
            result_file_path = self.result_sldem_path.joinpath(sldem_file_name)

            #Geotiffに変換したファイルがない時だけ作る
            if result_file_path.exists():
                pass
            else:
                cmd = ["gdal_translate",str(sldem), str(result_file_path)]
                subprocess.call(cmd)
    
    def downsampling_nac(self):
        # "加工後のlro nacを保存するディレクトリがないなら作る"
        if self.result_lro_nac_path.exists():
            pass
        else:
            self.result_lro_nac_path.mkdir()

        if self.result_lro_nac_tiff_path.exists():
            pass
        else:
            self.result_lro_nac_tiff_path.mkdir()

        for nac in self.nac_list:
            # 画像の解像度が得られる
            result_file_path = self.result_lro_nac_tiff_path.joinpath(str(nac.name))
            # 加工後の画像がないならdownsampling
            if result_file_path.exists():
                pass
            else:
                cmd = ["gdalwarp","-tr", "7.40", "7.40", "-r","near",str(nac), str(result_file_path)]
                subprocess.call(cmd)
    
    def nac2png(self):
        if self.result_lro_nac_png_path.exists():
            pass
        else:
            self.result_lro_nac_png_path.mkdir()

        for nac in list(self.result_lro_nac_path.glob(("**/*.tiff"))):
            file_name = pathlib.Path(nac).with_suffix(".png").name
            result_file_path = self.result_lro_nac_png_path.joinpath(str(file_name))
            
            if result_file_path.exists():
                pass
            else:
                cmd = ["gdal_translate","-of","PNG", "-ot", "Byte", "-scale",str(nac),str(result_file_path)]
                subprocess.call(cmd)
    
    def cut_geotiff(self):

        if self.result_cut_lro_nac_path.exists():
            pass
        else:
            self.result_cut_lro_nac_path.mkdir()

        for nac in list(self.result_lro_nac_tiff_path.glob("**/*.tiff")):
            origin_data = gdal.Open(str(nac))
            width = origin_data.RasterXSize # 画像の横
            height = origin_data.RasterYSize# 画像の縦
            data_info = origin_data.GetGeoTransform()
            # 小数点はカットしておく
            # 画像のy座標始端
            # x解像度とy解像度にそれぞれ縦、横をかけている
            # 画像の上を始端にしている
            """
            GetGeoTransform()で出力される数列の意味は、
            [始点端x座標（経度）,
            x方向（西東）解像度,
            回転,
            始点端y座標（緯度）,
            回転,
            y方向（南北）解像度（北南方向であれば負）] 
            start_x = int(data_info[0]) # 画像のx座標始端
            start_y = int(data_info[3] + width * data_info[4] + height * data_info[5])
            end_x = int(data_info[0] + width * data_info[1] + height * data_info[2])
            end_y = int(data_info[3])

            """
            cut_width = 256
            cut_height = 256
            cnt = 0
            
            for i in range(0,height,cut_height):
                for j in  range(0,width,cut_width):
                    result_file_path = self.result_cut_lro_nac_path.joinpath(str(cnt)+str(nac.name))
                    left_x = str(data_info[0] + j*data_info[1] + height * data_info[2])
                    bottom_y = str(data_info[3] + (j+cut_width)*data_info[4] + (i+cut_height) * data_info[5])
                    right_x = str(data_info[0] + (j+cut_width) * data_info[1] + (i+cut_height)*data_info[2])
                    top_y = str(data_info[3] + j*data_info[4] + i * data_info[5])
                    print(left_x,top_y,right_x,bottom_y)
                    if result_file_path.exists():
                        continue
                    else:
                        cmd = ["gdal_translate","-projwin",left_x,top_y,right_x,bottom_y,str(nac),str(result_file_path)]
                        subprocess.call(cmd)
                    cnt += 1

            """
            for i in range(start_y,end_y,cut_height):
                for j in range(start_x,end_x,cut_width):
                    result_file_path = self.result_cut_lro_nac_path.joinpath(str(cnt)+str(nac.name))
                    left_x = str(start_x+j)
                    bottom_y = str(start_y+i+cut_height*data_info[5])
                    right_x = str(start_x+j+cut_width*data_info[1])
                    top_y = str(start_y+i)
                    print(left_x,top_y,right_x,bottom_y)
                    if result_file_path.exists():
                        continue
                    else:
                        cmd = ["gdal_translate","-projwin",left_x,top_y,right_x,bottom_y,str(nac),str(result_file_path)]
                        subprocess.call(cmd)
                    cnt += 1
            """

if __name__ == "__main__":
    #元データのパスをプログラム実行時に指定する
    if len(sys.argv) > 1:
        dataset_process = DatasetProcess(sys.argv[1])
    #指定しないならDockerにマウントしてあるデータセットのoriginを参照する
    else:
        dataset_process = DatasetProcess(pathlib.Path("/","dataset","origin"))
    # dataset_process.sldem2geotiff()
    dataset_process.cut_geotiff()