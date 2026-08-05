#!/usr/bin/env python3
import argparse,sys
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]; sys.path.insert(0,str(ROOT/'src'))
from lithotwin.data import generate
import numpy as np
def main():
 p=argparse.ArgumentParser(); p.add_argument('--bases',type=int,default=420); p.add_argument('--conditions',type=int,default=8); p.add_argument('--seed',type=int,default=42); a=p.parse_args(); d=generate(a.bases,a.conditions,a.seed); (ROOT/'data').mkdir(exist_ok=True); np.savez_compressed(ROOT/'data/lithography.npz',**d); print({s:int((d['split']==s).sum()) for s in np.unique(d['split'])})
if __name__=='__main__': main()
