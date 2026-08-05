from __future__ import annotations
import numpy as np
from .simulator import make_mask,develop,GRID

FAMILIES=["line","line_end","space","elbow","dense","two_line","contact"]

def generate(n_bases=420,conditions_per_base=8,seed=42):
    rng=np.random.default_rng(seed); masks=[]; params=[]; labels=[]; aerials=[]; splits=[]; families=[]; base_ids=[]
    for base in range(n_bases):
        family=FAMILIES[base%len(FAMILIES)]; mask=make_mask(family,rng)
        if family=="contact": split="ood_geometry"
        elif base%10==0: split="test"
        elif base%10==1: split="val"
        else: split="train"
        for j in range(conditions_per_base):
            if j==conditions_per_base-1 and split!="ood_geometry":
                dose=float(rng.choice([.68,1.32])); focus=float(rng.choice([-1.8,1.8])); this_split="ood_process"
            else:
                dose=float(rng.uniform(.78,1.22)); focus=float(rng.uniform(-1.15,1.15)); this_split=split
            na=float(rng.uniform(.58,.72)); threshold=float(rng.uniform(.25,.48)); aerial,resist=develop(mask,dose,focus,na,threshold)
            masks.append(mask); params.append([dose,focus,na,threshold]); labels.append(resist); aerials.append(aerial); splits.append(this_split); families.append(family); base_ids.append(base)
    return {"masks":np.asarray(masks,np.float32),"params":np.asarray(params,np.float32),"resist":np.asarray(labels,np.float32),"aerial":np.asarray(aerials,np.float32),"split":np.asarray(splits),"family":np.asarray(families),"base_id":np.asarray(base_ids,int)}

def channels(masks,params):
    n,h,w=masks.shape; p=np.broadcast_to(params[:,:,None,None],(n,4,h,w)); return np.concatenate([masks[:,None],p],axis=1).astype(np.float32)
