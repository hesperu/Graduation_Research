import torch

# GAN の Adversarial 損失の定義 (Real/Fake識別)
class GANLoss(torch.nn.Module):
    def __init__(self):
        super().__init__()

        self.register_buffer("real_label",torch.tensor(1.0))
        self.register_buffer("fake_label",torch.tensor(0.0))

        #real/fake 識別の損失 BinaryCrossEntropy
        self.loss = torch.nn.BCEWithLogitsLoss()

    def __call__(self,prediction,is_real):
        if is_real:
            target_tensor = self.real_label
        else:
            target_tensor = self.fake_label
        
        return self.loss(prediction,target_tensor.expand_as(prediction))