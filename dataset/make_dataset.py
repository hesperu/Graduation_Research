import pathlib
import sys
import gdal
import subprocess

class DatasetProcess:
    def __init__(self,path):
        self.origin_data_path = path
        self.processed_path = self.origin_data_path.parent.joinpath("processed")
        self.sldem_list = []
        # 加工したデータセットのディレクトリが存在しないなら作る
        if self.processed_path.exists():
            pass
        else:
            self.processed_path.mkdir()
    
    def sldem2geotiff(self):
        self.sldem_list =list(self.origin_data_path.joinpath("sldem").glob("**/*.LBL"))
        self.result_sldem_path = self.processed_path.joinpath("sldem")
        "加工後のsldemを保存するディレクトリがないなら作る"
        if self.result_sldem_path.exists():
            pass
        else:
            self.result_sldem_path.mkdir()
        
        for sldem in self.sldem_list:
            sldem_file_name = pathlib.Path(sldem).with_suffix(".tif").name
            result_file_path = self.result_sldem_path.joinpath(sldem_file_name)
            cmd = ["gdal_translate",str(sldem), str(result_file_path)]
            subprocess.call(cmd)


if __name__ == "__main__":
    #元データのパスをプログラム実行時に指定する
    if len(sys.argv) > 1:
        dataset_process = DatasetProcess(sys.argv[1])
    #指定しないならDockerにマウントしてあるデータセットのoriginを参照する
    else:
        dataset_process = DatasetProcess(pathlib.Path("/","dataset","origin"))
    
    dataset_process.sldem2geotiff()