from genericpath import exists
from operator import le
import pathlib
import sys
from unittest import result
import gdal
import subprocess

class DatasetProcess:
    def __init__(self,path,sldem):
        """
        各ディレクトリの保存先の親ディレクトリは/mnt/ibuka_dataset/
        引数sldem,nacでデータ形式を指定
        sldem:sldem2013 or sldem2015 
        nac: lro_nac or lro_nac_mosaic
        """
        self.origin_data_path = path
        self.processed_path = self.origin_data_path.parent.joinpath("processed")
        self.dataset_path = self.origin_data_path.parent.joinpath("dataset")
        self.result_sldem_path = self.processed_path.joinpath(sldem)
        self.result_lro_nac_path = self.processed_path.joinpath(nac)
        self.result_lro_nac_png_path = self.result_lro_nac_path.joinpath("png")
        self.result_lro_nac_tiff_path = self.result_lro_nac_path.joinpath("tiff")
        self.result_cut_lro_nac_path = self.result_lro_nac_path.joinpath("cut")
        self.result_cut_sldem_path = self.result_sldem_path.joinpath("cut")
        self.result_cut_sldem_tiff_path = self.result_cut_sldem_path.joinpath("tiff")
        self.result_cut_sldem_png_path = self.result_cut_sldem_path.joinpath("png")
        self.result_cut_lro_nac_tiff_path = self.result_cut_lro_nac_path.joinpath("tiff")
        self.result_cut_lro_nac_png_path = self.result_cut_lro_nac_path.joinpath("png")
        self.sldem_list =list(self.origin_data_path.joinpath(sldem).glob("**/*"))
        
        self.nac_list = list(self.origin_data_path.joinpath(nac).glob("**/*"))
        # 加工したデータセットのディレクトリが存在しないなら作る
        if self.processed_path.exists():
            pass
        else:
            self.processed_path.mkdir()
        
        self.sldem_type = sldem
        self.nac_type = nac
    
    def sldem2geotiff(self):
        # "加工後のsldemを保存するディレクトリがないなら作る"
        if self.result_sldem_path.exists():
            pass
        else:
            self.result_sldem_path.mkdir()
            
        for sldem_dir in self.sldem_list:
            save_dir = self.result_sldem_path.joinpath(sldem_dir.name)
            
            if save_dir.exists():
                pass
            else:
                save_dir.mkdir()

            for sldem_file in list(sldem_dir.glob("**/*.lbl")):
                sldem_file_name = pathlib.Path(sldem_file).with_suffix(".tiff").name
                result_file_path = save_dir.joinpath(sldem_file_name)
                print(result_file_path)
                #Geotiffに変換したファイルがない時だけ作る
                if result_file_path.exists():
                    pass
                else:
                    cmd = ["gdal_translate",str(sldem_file), str(result_file_path)]
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

        x_resolution,y_resolution = (0,0)
        if self.sldem_type=="sldem2013":
            x_resolution,y_resolution = (7.40,7.40)
        elif self.sldem_type=="sldem2015":
            x_resolution,y_resolution = (59.225,59.225) #(118.45,118.45)
        else:
            print("not supported sldem")
            return

        for nac_dir in self.nac_list:
            # 画像の解像度が得られる
            result_dir_path = self.result_lro_nac_path.joinpath(nac_dir.name)
            if result_dir_path.exists():
                pass
            else:
                result_dir_path.mkdir()

            for nac in list(nac_dir.glob("**/*.TIF")):
                result_file_path = self.result_lro_nac_path.joinpath(str(nac_dir.name),str(nac.name))
                # 加工後の画像がないならdownsampling
                if result_file_path.exists():
                    pass
                else:
                    cmd = ["gdalwarp","-tr",str(x_resolution),str(y_resolution), "-r","near",str(nac), str(result_file_path)]
                    subprocess.call(cmd)
    
    def nac2png(self):
        if self.result_cut_lro_nac_png_path.exists():
            pass
        else:
            self.result_cut_lro_nac_png_path.mkdir()

        for nac in list(self.result_cut_lro_nac_tiff_path.glob(("**/*.tiff"))):
            file_name = pathlib.Path(nac).with_suffix(".png").name
            result_file_path = self.result_cut_lro_nac_png_path.joinpath(str(file_name))
            
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
        
        if self.result_cut_lro_nac_tiff_path.exists():
            pass
        else:
            self.result_cut_lro_nac_tiff_path.mkdir()
        
        if self.result_cut_sldem_path.exists():
            pass
        else:
            self.result_cut_sldem_path.mkdir()

        if self.result_cut_sldem_png_path.exists():
            pass
        else:
            self.result_cut_sldem_png_path.mkdir()
        
        if self.result_cut_sldem_tiff_path.exists():
            pass
        else:
            self.result_cut_sldem_tiff_path.mkdir()

        for nac_dir in list(self.result_lro_nac_path.glob("**/*")):
            for nac in list(nac_dir.glob("**/*.TIF")):
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
                """
                cut_width = 256
                cut_height = 256
                cnt = 0
                start_x = int(data_info[0]) # 画像のx座標始端
                end_y = int(data_info[3] + width * data_info[4] + height * data_info[5])
                end_x = int(data_info[0] + width * data_info[1] + height * data_info[2])
                start_y = int(data_info[3])

                for i in range(0,height,cut_height):
                    for j in  range(0,width,cut_width):
                        result_file_path = self.result_cut_lro_nac_tiff_path.joinpath(str(cnt)+str(nac.name))
                        sldem_result_file_path = self.result_cut_sldem_tiff_path.joinpath(str(cnt)+str(nac.name))
                        left_x = data_info[0] + j*data_info[1] + height * data_info[2]
                        bottom_y = data_info[3] + (j+cut_width)*data_info[4] + (i+cut_height) * data_info[5]
                        right_x = data_info[0] + (j+cut_width) * data_info[1] + (i+cut_height)*data_info[2]
                        top_y = data_info[3] + j*data_info[4] + i * data_info[5]
                        print("nacの左x,上y,右x,下y")
                        print(left_x,top_y,right_x,bottom_y)

                        sldem_path = self.find_sldem(left_x,top_y,right_x,bottom_y)
                
                        if not sldem_path:
                            print("nacに対応しているsldem見つからなかった!")
                            continue
                        else:
                            print("{nac}に対応しているファイルは{sldem}だね".format(nac=nac,sldem=sldem_path))
                        
                        if result_file_path.exists():
                            continue
                        else:
                            cmd = ["gdal_translate","-projwin",str(left_x),str(top_y),str(right_x),str(bottom_y),str(nac),str(result_file_path)]
                            subprocess.call(cmd)
                        
                            sldem_data = gdal.Open(str(sldem_path))
                            sldem_width = sldem_data.RasterXSize # 画像の横
                            sldem_height = sldem_data.RasterYSize# 画像の縦
                            sldem_data_info = sldem_data.GetGeoTransform()
                            sldem_left_x = str(sldem_data_info[0] + j*sldem_data_info[1] + sldem_height * sldem_data_info[2])
                            sldem_bottom_y = str(sldem_data_info[3] + (j+cut_width)*sldem_data_info[4] + (i+cut_height) * sldem_data_info[5])
                            sldem_right_x = str(sldem_data_info[0] + (j+cut_width) * sldem_data_info[1] + (i+cut_height)* sldem_data_info[2])
                            sldem_top_y = str(sldem_data_info[3] + j*sldem_data_info[4] + i * sldem_data_info[5])
                            print("sldem")
                            print(left_x,top_y,right_x,bottom_y)
                            cmd = ["gdal_translate","-projwin",str(left_x),str(top_y),str(right_x),str(bottom_y),str(sldem_path),str(sldem_result_file_path)]
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

    
    def find_sldem(self,nac_start_x,nac_start_y,nac_end_x,nac_end_y):
        """
        NACのgeotiffの位置情報を元にして、それを内包しているsldemを探してくる
        戻り値は内包しているsldemのパス,見つからないときはFalse
        """
        for sldem_dir in list(self.result_sldem_path.glob("**/lon*")):
            for sldem in list(sldem_dir.glob("**/*.tiff")):
                data = gdal.Open(str(sldem))
                width = data.RasterXSize # 画像の横
                height = data.RasterYSize# 画像の縦
                data_info = data.GetGeoTransform()
                sldem_start_x = int(data_info[0]) # 画像のx座標始端
                sldem_start_y = int(data_info[3])
                sldem_end_x = int(data_info[0] + width * data_info[1] + height * data_info[2])
                sldem_end_y = int(data_info[3] + width * data_info[4] + height * data_info[5])
                """
                print("nacの情報")
                print(nac_start_x,nac_start_y,nac_end_x,nac_end_y)
                print("sldemの情報")
                print(sldem_start_x,sldem_start_y,sldem_end_x,sldem_end_y)
                """
                if (sldem_start_x <= nac_start_x) and (nac_start_y <= sldem_start_y) and (sldem_end_x >= nac_end_x) and (sldem_end_y <= nac_end_y):
                    """
                    print("sldemの左x,上y,右x,下y")
                    """
                    print("nacの情報")
                    print(nac_start_x,nac_start_y,nac_end_x,nac_end_y)
                    print("sldemの情報")
                    print(sldem_start_x,sldem_start_y,sldem_end_x,sldem_end_y)
                    print(sldem) 
                    return sldem               
                else:
                    pass
            
        return False
    
    def geotiff2png(self):
        """
        geotiffからpngを生成する
        data_typeはsldem、nacのどちらかを見る
        """

        if self.result_cut_lro_nac_png_path.exists():
            pass
        else:
            self.result_cut_lro_nac_png_path.mkdir()

        for nac_path in list(self.result_cut_lro_nac_tiff_path.glob("*.TIF")):
            result_path = self.result_cut_lro_nac_png_path.joinpath(nac_path.with_suffix(".png").name)
            cmd = ["gdal_translate","-of","PNG","-ot","Byte","-scale",str(nac_path),str(result_path)]
            subprocess.call(cmd)


        if self.result_cut_sldem_png_path.exists():
            pass
        else:
            self.result_cut_sldem_png_path.mkdir()
        
        for sldem_path in list(self.result_cut_sldem_tiff_path.glob("*.TIF")):
            result_path = self.result_cut_sldem_png_path.joinpath(sldem_path.with_suffix(".png").name)
            cmd = ["gdal_translate","-of","PNG","-ot","UInt16","-scale",str(sldem_path),str(result_path)]
            subprocess.call(cmd)
    
    def remove_disused(self):
        """
        cutgeotiffをやると黒い隙間がある画像が生成されるときがある。
        lro_nacの方でそれを目視で削除する。
        lro_nacの方にsldemと同じ位置の画像がないなら削除をする。
        """
        for sldem_path in list(self.result_cut_sldem_tiff_path.glob("*.TIF")):
            file_name = sldem_path.name

            if self.result_cut_lro_nac_tiff_path.joinpath(file_name).exists():
                pass
            else:
                print(file_name)
                sldem_path.unlink(missing_ok=False)

    def data_augmentation(self):
        """
        画像の水増し
        対象とするのはsldem2015を使う場合だけ
        """
        if self.sldem_type == "sldem2013":
            return
        
               

if __name__ == "__main__":
    #元データのパスをプログラム実行時に指定する
    if len(sys.argv) > 1:
        dataset_process = DatasetProcess(sys.argv[1],str(sys.argv[2],str(sys.argv[3])))
    #指定しないならDockerにマウントしてあるデータセットのoriginを参照する
    else:
        dataset_process = DatasetProcess(pathlib.Path("/","dataset","ssd4T","ibuka_dataset","origin"),"sldem2013","nac_mosaic")
    # dataset_process.sldem2geotiff()
    # dataset_process.downsampling_nac()
    # dataset_process.cut_geotiff()
    # dataset_process.remove_disused()
    # dataset_process.geotiff2png()
