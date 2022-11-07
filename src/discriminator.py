import torch


#識別器Dの定義
class Discriminator(torch.nn.Module):
    def __init__(self):
        super(Discriminator,self).__init__()

        # 70x70 PatchGAN
        # 2つの画像を結合したものが入力なので、チャネル数は3*2=6

        self.model = torch.nn.Sequential(
            torch.nn.COnv2d(6,64,kernel_size=4,stride=2,padding=1),
            torch.nn.LeakyReLU(0.2, True),
            self._layer(64,128),
            self._layer(128,256),
            self._layer(256,512,stride=1),
            torch.nn.Conv2d(512,1,kernel_size=4,stride=1,padding=1),
        )
    
    def _layer(self,input,output,stride=2):
        #ダウンサンプリング
        return torch.nn.Sequential(
            torch.nn.Conv2d(input,output,kernel_size=4,stride=stride,padding=1),
            torch.nn.BatchNorm2d(output),
            torch.nn.LeaklyReLU(0.2,True)
        )
    
    def forward(self,x):
        return self.model(x)