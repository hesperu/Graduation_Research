import torch
import torchvision
import tor
class Generator(torch.nn.Module):
    def __init__(self):
        super(Generator,self).__init__()
        # U-Netのエンコーダー
        self.down0 = torch.nn.Conv2d(3,64,kernel_size=4,stride=2,padding=1)
        self.down1 = self._encoder_block(64,128)
    
    def _encoder_block(self,input,output,use_norm=True):
        # LeakyReLU + Downsampling
        layer = [
            torch.nn.LeakyReLU(0.2, TRue)
            torch.nn.Conv2d(input,output)
        ]
        # BatchNormalization
        if use_norm:
            layer.append(torch.nn.BathNorm2d(output))
        
        return torch.nn.Sequential(*layer)

    def _decoder_block(self,input,output,use_norm=True,use_dropout=False):
        # ReLU + Upsampling
        layer = [
            torch.nn.ReLU(True),
            torch.nn.ConvTranspose2d(input,output,kernel_size=4,stride=2,padding=1)
        ]
        # BatchNormalization
        if use_norm:
            layer.append(torch.nn.BatchNorm2d(output))
        #Dropout
        if use_dropout:
            layer.append(torch.nn.Dropout(0.5))
        return torch.nn.Sequential(*layer)

    def forward(self,x):
        # 偽物画像の生成を行う
        x0 = self.down0(x)
        x1 = self.down1(x0)
        x2 = self.down2(x1)
        x3 = self.down3(x2)
        x4 = self.down4(x3)
        x5 = self.down5(x4)
        x6 = self.down6(x5)
        x7 = self.down7(x6)
        y7 = self.up7(x7)

        # Encoderの出力をDecoderの入力にSkipConnectionで接続
        y6 = self.up6(self.concat(x6,y7))
        y5 = self.up5(self.concat(x5,y6))
        y4 = self.up4(self.concat(x4,y5))
        y3 = self.up3(self.concat(x3,y4))
        y2 = self.up2(self.concat(x2,y3))
        y1 = self.up1(self.concat(x1,y2))
        y0 = self.up0(self.concat(x0,y1))

        return y0

    def concat(self,x,y):
        return torch.cat([x,y],dim=1)