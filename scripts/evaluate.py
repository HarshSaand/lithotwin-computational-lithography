#!/usr/bin/env python3
from __future__ import annotations
import json,sys,time
from pathlib import Path
import numpy as np,torch
ROOT=Path(__file__).resolve().parents[1]; sys.path.insert(0,str(ROOT/'src'))
from lithotwin.data import channels
from lithotwin.model import ConditionalUNet
from lithotwin.simulator import metrics,gaussian_baseline,develop
def summarize(ref,pred):
 vals=[metrics(r,p) for r,p in zip(ref,pred)]; return {k:float(np.mean([v[k] for v in vals])) for k in vals[0]}
def main():
 d=np.load(ROOT/'data/lithography.npz'); ck=torch.load(ROOT/'artifacts/lithotwin.pt',map_location='cpu',weights_only=False); model=ConditionalUNet(**ck['config']); model.load_state_dict(ck['state_dict']); model.eval(); out={}
 for split in ('test','ood_process','ood_geometry'):
  ids=np.where(d['split']==split)[0]; x=torch.from_numpy(channels(d['masks'][ids],d['params'][ids])); t=time.perf_counter()
  with torch.no_grad(): prob=torch.sigmoid(model(x)).numpy()[:,0]
  ai_us=(time.perf_counter()-t)/len(ids)*1e6; pred=prob>=.5; base=np.asarray([gaussian_baseline(m,*[float(v) for v in p[[0,1,3]]]) for m,p in zip(d['masks'][ids],d['params'][ids])]); t=time.perf_counter(); [develop(m,float(p[0]),float(p[1]),float(p[2]),float(p[3])) for m,p in zip(d['masks'][ids],d['params'][ids])]; sim_us=(time.perf_counter()-t)/len(ids)*1e6
  # MC-dropout disagreement and pixelwise Brier calibration proxy.
  model.train(); draws=[]
  with torch.no_grad():
   for _ in range(6): draws.append(torch.sigmoid(model(x)).numpy()[:,0])
  uncertainty=np.stack(draws).std(0).mean((1,2)); err=np.asarray([1-metrics(r,p)['iou'] for r,p in zip(d['resist'][ids],pred)])
  out[split]={'n':len(ids),'ai':summarize(d['resist'][ids],pred),'baseline':summarize(d['resist'][ids],base),'brier':float(np.mean((prob-d['resist'][ids])**2)),'uncertainty_error_correlation':float(np.corrcoef(uncertainty,err)[0,1]),'ai_us_per_clip':ai_us,'simulator_us_per_clip':sim_us,'measured_speedup':sim_us/max(ai_us,1e-9)}
 (ROOT/'outputs').mkdir(exist_ok=True); (ROOT/'outputs/metrics.json').write_text(json.dumps(out,indent=2)); print(json.dumps(out,indent=2))
if __name__=='__main__': main()
