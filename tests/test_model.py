import torch
from lithotwin.model import ConditionalUNet,dice_loss
def test_model_shape_and_loss():
 m=ConditionalUNet(); x=torch.rand(2,5,48,48); y=(torch.rand(2,1,48,48)>.5).float(); z=m(x); assert z.shape==y.shape; assert 0<=dice_loss(z,y)<=1
