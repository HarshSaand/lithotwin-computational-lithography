from __future__ import annotations
import torch
from torch import nn
import torch.nn.functional as F

class Block(nn.Module):
    def __init__(self,a,b): super().__init__(); self.net=nn.Sequential(nn.Conv2d(a,b,3,padding=1),nn.BatchNorm2d(b),nn.SiLU(),nn.Conv2d(b,b,3,padding=1),nn.BatchNorm2d(b),nn.SiLU())
    def forward(self,x): return self.net(x)

class ConditionalUNet(nn.Module):
    def __init__(self,in_channels=5,width=16,dropout=.15):
        super().__init__(); self.e1=Block(in_channels,width); self.e2=Block(width,width*2); self.b=Block(width*2,width*4); self.d2=Block(width*4+width*2,width*2); self.d1=Block(width*2+width,width); self.drop=nn.Dropout2d(dropout); self.out=nn.Conv2d(width,1,1)
    def forward(self,x):
        e1=self.e1(x); e2=self.e2(F.max_pool2d(e1,2)); b=self.drop(self.b(F.max_pool2d(e2,2))); d2=self.d2(torch.cat([F.interpolate(b,scale_factor=2,mode='bilinear',align_corners=False),e2],1)); d1=self.d1(torch.cat([F.interpolate(d2,scale_factor=2,mode='bilinear',align_corners=False),e1],1)); return self.out(d1)

def dice_loss(logits,target):
    p=torch.sigmoid(logits); inter=(p*target).sum((1,2,3)); return (1-(2*inter+1)/(p.sum((1,2,3))+target.sum((1,2,3))+1)).mean()
