import subprocess
import sys
import pathlib
"""
保存先のディレクトリと、lonの何番目からダウンロードするか指定する
"""
def get_sldem(save_dir_parent,num=0):
    for i in range(num,360):
        save_dir = pathlib.Path(save_dir_parent).joinpath("lon"+str(i).zfill(3))
        
        if save_dir.exists():
            pass
        else:
            save_dir.mkdir()
        
        cmd = ["wget", "--continue","-r","-l", "1", "-A","img,lbl","-w","5","-nd",
        "-P", str(save_dir),
        "https://data.darts.isas.jaxa.jp/pub/pds3/sln-l-tc-5-sldem2013-v1.0/lon"+str(i).zfill(3)+"/data/"]
        subprocess.call(cmd)

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Argumenr path error")
        print(len(sys.argv))
    else:    
        get_sldem(sys.argv[1],int(sys.argv[2]))