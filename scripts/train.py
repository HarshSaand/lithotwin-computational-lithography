#!/usr/bin/env python3
from __future__ import annotations
import argparse,json,random,sys,time
from pathlib import Path
import numpy as np,torch
from torch.utils.data import TensorDataset,DataLoader
ROOT=Path(__file__).resolve().parents[1]; sys.path.insert(0,str(ROOT/'src'))
from lithotwin.data import channels
from lithotwin.model import ConditionalUNet,dice_loss
def main():
 p=argparse.ArgumentParser(); p.add_argument('--epochs',type=int,default=12); p.add_argument('--seed',type=int,default=42); p.add_argument('--batch-size',type=int,default=64); p.add_argument('--device',default='cpu'); a=p.parse_args(); random.seed(a.seed); np.random.seed(a.seed); torch.manual_seed(a.seed)
 d=np.load(ROOT/'data/lithography.npz'); x=channels(d['masks'],d['params']); y=d['resist'][:,None]; ids={s:np.where(d['split']==s)[0] for s in ('train','val')}; loaders={s:DataLoader(TensorDataset(torch.from_numpy(x[i]),torch.from_numpy(y[i])),batch_size=a.batch_size,shuffle=s=='train') for s,i in ids.items()}; dev=torch.device(a.device); model=ConditionalUNet().to(dev); opt=torch.optim.AdamW(model.parameters(),lr=2e-3,weight_decay=1e-4); bce=torch.nn.BCEWithLogitsLoss(); best=None; history=[]
 for epoch in range(a.epochs):
  model.train(); total=0
  for xb,yb in loaders['train']:
   xb,yb=xb.to(dev),yb.to(dev); opt.zero_grad(); z=model(xb); loss=bce(z,yb)+dice_loss(z,yb); loss.backward(); opt.step(); total+=loss.item()*len(xb)
  model.eval(); vl=0
  with torch.no_grad():
   for xb,yb in loaders['val']:
    xb,yb=xb.to(dev),yb.to(dev); z=model(xb); vl+=(bce(z,yb)+dice_loss(z,yb)).item()*len(xb)
  row={'epoch':epoch+1,'train_loss':total/len(ids['train']),'val_loss':vl/len(ids['val'])}; history.append(row); print(json.dumps(row))
  if best is None or row['val_loss']<best[0]: best=(row['val_loss'],{k:v.detach().cpu().clone() for k,v in model.state_dict().items()})
 (ROOT/'artifacts').mkdir(exist_ok=True); torch.save({'state_dict':best[1],'config':{'in_channels':5,'width':16,'dropout':.15},'seed':a.seed,'history':history},ROOT/'artifacts/lithotwin.pt')
if __name__=='__main__': main()
