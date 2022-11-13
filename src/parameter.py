import json
import torch

class Opts():
    def __init__(self):
        self.epochs = 100
        self.save_data_interval = 10
        self.save_image_interval = 10
        self.log_interval = 20
        self.sample_interval = 10
        self.batch_size = 8
        self.load_size = 286
        self.crop_size = 256
        self.cpu = True
        self.dataroot = "/dataset/pix2pix_training"
        self.output_dir = './output'
        self.log_dir = './logs'
        self.lambda_L1 = 100.0
        self.epochs_lr_decay = 0
        self.epochs_lr_decay_start = -1
        self.path_to_discriminator = None
        self.path_to_generator = None
        self.device_name = "cuda"
        self.device = torch.device(self.device_name)
        
    def to_dict(self):
        parameters = {
            'epochs': self.epochs,
            'save_data_interval': self.save_data_interval,
            'save_image_interval': self.save_image_interval,
            'log_interval': self.log_interval,
            'sample_interval': self.sample_interval,
            'batch_size': self.batch_size,
            'load_size': self.load_size,
            'crop_size': self.crop_size,
            'cpu': self.cpu,
            'dataroot': self.dataroot,
            'output_dir' : self.output_dir,
            'log_dir': self.log_dir,
            'lambda_L1': self.lambda_L1,
            'epochs_lr_decay': self.epochs_lr_decay,
            'epochs_lr_decay_start': self.epochs_lr_decay_start,
            'path_to_generator': self.path_to_generator,
            'path_to_discriminator': self.path_to_discriminator,
            'device_name': self.device_name
        }
        return parameters
    
    def save_json(self,save_path,mode='w'):
        with open(save_path, mode) as outfile:
            json.dump(self.to_dict(),outfile,indent=4)
