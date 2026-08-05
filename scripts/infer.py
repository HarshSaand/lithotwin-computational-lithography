#!/usr/bin/env python3
import argparse,json,sys
from pathlib import Path
import numpy as np,torch
ROOT=Path(__file__).resolve().parents[1]; sys.path.insert(0,str(ROOT/'src'))
from lithotwin.data import channels
from lithotwin.model import ConditionalUNet
from lithotwin.simulator import develop,metrics
def main():
 p=argparse.ArgumentParser(); p.add_argument('--index',type=int,default=0); a=p.parse_args(); d=np.load(ROOT/'data/lithography.npz'); ck=torch.load(ROOT/'artifacts/lithotwin.pt',map_location='cpu',weights_only=False); model=ConditionalUNet(**ck['config']); model.load_state_dict(ck['state_dict']); model.eval(); i=a.index
 with torch.no_grad(): prob=torch.sigmoid(model(torch.from_numpy(channels(d['masks'][i:i+1],d['params'][i:i+1])))).numpy()[0,0]
 print(json.dumps({'index':i,'family':str(d['family'][i]),'split':str(d['split'][i]),'params':d['params'][i].tolist(),'metrics':metrics(d['resist'][i],prob>=.5)},indent=2))
if __name__=='__main__': main()
