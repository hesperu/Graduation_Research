import pathlib
import sys
import gdal
import subprocess

class DatasetProcess:
    def __init__(self,path):
        self.origin_data_path = path
        self.processed_path = self.origin_data_path.parent.joinpath("processed")
        self.dataset_path = self.origin_data_path.parent.joinpath("dataset")
        self.sldem_list =list(self.origin_data_path.joinpath("sldem").glob("**/*.LBL"))
        self.nac_list = list(self.origin_data_path.joinpath("lro_nac").glob("**/*.tiff"))
        # 加工したデータセットのディレクトリが存在しないなら作る
        if self.processed_path.exists():
            pass
        else:
            self.processed_path.mkdir()
    
    def sldem2geotiff(self):
        self.result_sldem_path = self.processed_path.joinpath("sldem")
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
        self.result_lro_nac_path = self.processed_path.joinpath("lro_nac")
        # "加工後のlro nacを保存するディレクトリがないなら作る"
        if self.result_lro_nac_path.exists():
            pass
        else:
            self.result_lro_nac_path.mkdir()

        self.result_lro_nac_tiff_path = self.result_lro_nac_path.joinpath("tiff")
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
        self.result_lro_nac_png_path = self.result_lro_nac_path.joinpath("png")

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

if __name__ == "__main__":
    #元データのパスをプログラム実行時に指定する
    if len(sys.argv) > 1:
        dataset_process = DatasetProcess(sys.argv[1])
    #指定しないならDockerにマウントしてあるデータセットのoriginを参照する
    else:
        dataset_process = DatasetProcess(pathlib.Path("/","dataset","origin"))
    # dataset_process.sldem2geotiff()
    dataset_process.downsampling_nac()
    dataset_process.nac2png()