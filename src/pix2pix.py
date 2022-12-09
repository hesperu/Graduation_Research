from torch.utils.tensorboard import SummaryWriter
import time
import torch
import torchvision
import pathlib

#ここから自作クラスのインポート
import generator
import loss
import discriminator
import parameter
import dataset

class Pix2Pix():
    def __init__(self, config):
        self.config = config

        #生成器G
        self.netG = generator.Generator().to(self.config.device)
        if self.config.device_name == "cuda":
            self.netG  = torch.nn.DataParallel(self.netG) # make parallel
            torch.backends.cudnn.benchmark = True

        #generatorの全ての関数を初期化
        self.netG.apply(self._weight_init)

        #識別器 D
        self.netD = discriminator.Discriminator().to(self.config.device)
        if self.config.device_name == "cuda":
            self.netD  = torch.nn.DataParallel(self.netD) # make parallel
            torch.backends.cudnn.benchmark = True

        #discriminatorのすべての関数を初期化
        self.netD.apply(self._weight_init)

        # 生成器 G のモデルファイル読み込み(学習を引き続き行う場合)
        if self.config.path_to_generator != None:
            self.netG.load_state_dict(torch.load(self.config.path_to_generator, map_location=self.config.device_name), strict=False)

        # D のモデルファイル読み込み(学習を引き続き行う場合)
        if self.config.path_to_discriminator != None:
            self.netD.load_state_dict(torch.load(self.config.path_to_discriminator, map_location=self.config.device_name), strict=False)

        # Optimizer, GとDそれぞれで
        self.optimizerG = torch.optim.Adam(self.netG.parameters(), lr=0.0002, betas=(0.5,0.999))
        self.optimizerD = torch.optim.Adam(self.netD.parameters(), lr=0.0002, betas=(0.5,0.999))

        #目的関数（損失関数)の設定
        #GAN損失, Adversarial損失
        self.criterionGAN = loss.GANLoss().to(self.config.device)
        #L1 損失
        self.criterionL1 = torch.nn.L1Loss()

        #学習率のスケジューラ設定
        self.schedulerG = torch.optim.lr_scheduler.LambdaLR(self.optimizerG,self._modify_learning_rate)
        self.schedulerD = torch.optim.lr_scheduler.LambdaLR(self.optimizerD,self._modify_learning_rate)
        
        #学習時間の記録は大事だよね
        self.training_start_time = time.time()

        #ログは取っておきましょう。大事だからね
        self.writer = SummaryWriter(log_dir=config.log_dir)

    def update_learning_rate(self):
        self.schedulerG.step()
        self.schedulerD.step()

    def _modify_learning_rate(self,epoch):
        #学習率の計算するよ
        if self.config.epochs_lr_decay_start < 0:
            return 1.0
        
        delta = max(0, epoch - self.config.epochs_lr_decay_start) / float(self.config.epochs_lr_decay)
        return max(0.0, 1.0 - delta)
    
    def _weight_init(self,m):
        #重みの初期化
        classname = m.__class__.__name__
        if classname.find("Conv") != -1:
            m.weight.data.normal_(0.0,0.02)
        elif classname.find("BatchNorm") != -1:
            m.weight.data.normal_(1.0,0.02)
            m.bias.data.fill_(0)
    
    def train(self,data,batches_done):
        #ドメインAのラベル画像とドメインBの正解画像を設定する
        self.realA = data['A'].to(self.config.device)
        self.realB = data['B'].to(self.config.device)

        #生成器GでドメインBの画像生成
        fakeB = self.netG(self.realA)

        #Discriminator
        #条件画像(A)と生成画像（B）を結合するよ
        fakeAB = torch.cat((self.realA,fakeB),dim=1)
        #識別器Dに生成画像を入力、この時Gは更新しないのでdetach(新しいテンソルを作成)、勾配は計算しない
        pred_fake = self.netD(fakeAB.detach())
        #偽物画像を入力した時の識別器DのGAN損失を算出
        lossD_fake = self.criterionGAN(pred_fake,False)

        #条件画像(A)と正解画像(B)を結合
        realAB = torch.cat((self.realA,fakeB), dim=1)
        #識別器Dに生成画像を入力
        pred_real = self.netD(realAB)
        # 正解画像を入力した時の識別器DのGAN損失を算出
        lossD_real = self.criterionGAN(pred_real,True)

        #偽画像と正解画像のGAN損失の合計に0.5をかける
        lossD = (lossD_fake + lossD_real) * 0.5

        #Dの勾配をゼロに設定
        self.optimizerD.zero_grad()
        #Dの逆伝播を計算
        lossD.backward(retain_graph=True)
        #Dの重みを更新する
        self.optimizerD.step()

        #Generator
        #評価なので勾配計算なし
        #識別器Dに生成画像を入力する
        with torch.no_grad():
            pred_fake = self.netD(fakeAB)
        
        #生成器GのGAN損失を算出
        lossG_GAN = self.criterionGAN(pred_fake,True)
        #生成器GのL1損失を算出
        lossG_L1 = self.criterionL1(fakeB,self.realB) * self.config.lambda_L1

        #生成器Gの損失を合計
        lossG = lossG_GAN + lossG_L1

        #Gの勾配をゼロに設定
        self.optimizerG.zero_grad()
        #Gの逆伝搬を計算
        lossG.backward(retain_graph=True)
        #Gの重みを更新
        self.optimizerG.step()

        # for log
        self.fakeB = fakeB
        self.lossG_GAN = lossG_GAN
        self.lossG_L1 = lossG_L1
        self.lossG = lossG
        self.lossD_real = lossD_real
        self.lossD_fake = lossD_fake
        self.lossD = lossD

        train_info = {
            "epoch" : epoch,
            "batch_num" : lossG_GAN.item(),
            "lossG_L1" : lossG_L1.item(),
            "lossG" : lossG.item(),
            "lossD_real" : lossD_real.item(),
            "lossD_fake" : lossD_fake.item(),
            "lossD" : lossD.item()
        }

        self.save_loss(train_info,batches_done)
    
    def save_model(self,epoch):
        #モデルの保存をしておく
        output_dir = self.config.output_dir
        torch.save(self.netG.state_dict(),"{output_dir}/pix2pix_G_epoch_{epoch}".format(output_dir=output_dir,epoch=epoch))
        torch.save(self.netD.state_dict(),"{output_dir}/pix2pix_D_epoch_{epoch}".format(output_dir=output_dir,epoch=epoch))

    def save_image(self,epoch):
        #条件画像、生成画像、正解画像を並べて画像を保存
        output_image = torch.cat([self.realA, self.fakeB, self.realB],dim=3)
        torchvision.utils.save_image(output_image,"{output_dir}/pix2pix_epoch_{epoch}.tiff".format(output_dir=self.config.output_dir,epoch=epoch),normalize=True)
        self.writer.add_image("image_epoch{epoch}".format(epoch=epoch),self.fakeB[0],epoch)
    
    def save_loss(self, train_info, batches_done):
        for k, v in train_info.items():
            self.writer.add_scalar(k,v,batches_done)


if __name__ == "__main__":
    opt = parameter.Opts()
    param_save_path = pathlib.Path(__file__).parent.joinpath("output","parameter.json")
    opt.save_json(str(param_save_path))

    model = Pix2Pix(opt)
    dataset = dataset.AlignedDataset(opt)
    dataloader = torch.utils.data.DataLoader(dataset,batch_size=opt.batch_size,shuffle=True)

    import random

    for epoch in range(1, opt.epochs + 1):
        for batch_num, data in enumerate(dataloader):
            batches_done = (epoch - 1) * len(dataloader) + batch_num
            model.train(data,batches_done)

            if batch_num % opt.log_interval == 0:
                print(f'===> Epoch[{epoch}]({batch_num}/{len(dataloader)}): Loss_D: {model.lossD_real:.4f} Loss_G: {model.lossG_GAN:.4f}')
            
            if epoch % opt.save_data_interval == 0:
                model.save_model(epoch)

            if epoch % opt.save_image_interval == 0:
                model.save_image(epoch)

        model.update_learning_rate()
