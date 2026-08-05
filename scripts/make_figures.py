#!/usr/bin/env python3
from pathlib import Path
import json,sys
import numpy as np,torch,matplotlib.pyplot as plt,seaborn as sns
ROOT=Path(__file__).resolve().parents[1]; sys.path.insert(0,str(ROOT/'src')); OUT=ROOT/'outputs/figures'; OUT.mkdir(parents=True,exist_ok=True)
from lithotwin.data import channels
from lithotwin.model import ConditionalUNet
from lithotwin.simulator import develop,metrics
sns.set_theme(style='whitegrid'); navy='#082B4C'; teal='#00A6A6'; gold='#E4B363'; red='#D1495B'
d=np.load(ROOT/'data/lithography.npz'); ck=torch.load(ROOT/'artifacts/lithotwin.pt',map_location='cpu',weights_only=False); model=ConditionalUNet(**ck['config']); model.load_state_dict(ck['state_dict']); model.eval(); m=json.loads((ROOT/'outputs/metrics.json').read_text())

ids=np.where(d['split']=='test')[0]; i=ids[len(ids)//3]; x=torch.from_numpy(channels(d['masks'][i:i+1],d['params'][i:i+1]));
with torch.no_grad(): prob=torch.sigmoid(model(x)).numpy()[0,0]
pred=prob>=.5; panels=[(d['masks'][i],'Mask','gray'),(d['aerial'][i],'Aerial image','viridis'),(d['resist'][i],'Reference resist','gray'),(prob,'AI probability','viridis'),(pred.astype(float)-d['resist'][i],'Signed error','coolwarm')]
fig,axs=plt.subplots(1,5,figsize=(12,2.7));
for ax,(im,title,cmap) in zip(axs,panels): ax.imshow(im,cmap=cmap,vmin=-1 if title=='Signed error' else None,vmax=1 if title=='Signed error' else None); ax.set_title(title,fontsize=10); ax.axis('off')
fig.suptitle('Representative geometry-grouped test case',weight='bold',color=navy); plt.tight_layout(); fig.savefig(OUT/'prediction_panel.png',dpi=200); plt.close(fig)

splits=['test','ood_process','ood_geometry']; labels=['Held-out\ngeometries','Process-range\nOOD','Unseen contact\nfamily']; ai=[m[s]['ai']['iou'] for s in splits]; base=[m[s]['baseline']['iou'] for s in splits]; x=np.arange(3); fig,ax=plt.subplots(figsize=(7,4.5)); w=.35; ax.bar(x-w/2,base,w,label='Gaussian baseline',color=gold); ax.bar(x+w/2,ai,w,label='Conditional U-Net',color=teal); ax.set_xticks(x,labels); ax.set_ylim(0,1); ax.set_ylabel('Mean IoU'); ax.set_title('Contour fidelity by evaluation regime',weight='bold',color=navy); ax.legend(); ax.bar_label(ax.containers[0],fmt='%.3f'); ax.bar_label(ax.containers[1],fmt='%.3f'); plt.tight_layout(); fig.savefig(OUT/'iou_comparison.png',dpi=180); plt.close(fig)

# Dose-focus process window: physics and AI printed-area fractions.
mask=d['masks'][i]; na=.65; th=.35; doses=np.linspace(.78,1.22,13); focuses=np.linspace(-1.15,1.15,13); phys=np.zeros((13,13)); aiw=np.zeros_like(phys)
records=[]
for a,f in enumerate(focuses):
 for b,dose in enumerate(doses):
  _,r=develop(mask,float(dose),float(f),na,th); phys[a,b]=r.mean(); records.append([dose,f,na,th])
xx=np.repeat(mask[None],len(records),0)
with torch.no_grad(): pp=torch.sigmoid(model(torch.from_numpy(channels(xx,np.asarray(records,np.float32))))).numpy()[:,0]
aiw=pp.mean((1,2)).reshape(13,13); fig,axs=plt.subplots(1,3,figsize=(11,3.6));
for ax,z,title in zip(axs,[phys,aiw,np.abs(aiw-phys)],['Physics printed area','AI printed area','Absolute area error']): im=ax.imshow(z,origin='lower',aspect='auto',extent=[doses[0],doses[-1],focuses[0],focuses[-1]],cmap='viridis'); fig.colorbar(im,ax=ax); ax.set(xlabel='Relative dose',ylabel='Defocus',title=title)
fig.suptitle('Dose-focus process window',weight='bold',color=navy); plt.tight_layout(); fig.savefig(OUT/'process_window.png',dpi=180); plt.close(fig)

fig,ax=plt.subplots(figsize=(7,7)); ax.axis('off'); boxes=[('1  Mask + recipe DOE','Seven geometry families; dose, focus, NA, threshold'),('2  Reference optics','Nine-source scalar Abbe imaging + threshold resist'),('3  Leakage-safe partitions','Base geometries remain in one data split'),('4  Conditional neural surrogate','Mask + four process channels -> resist contour'),('5  Engineering evaluation','IoU, Dice, edge distance, area, calibration, OOD'),('6  Engineer review output','Contour overlays, process window, uncertainty flag')]; ys=np.linspace(.9,.1,len(boxes))
for j,((a,b),y) in enumerate(zip(boxes,ys)):
 ax.add_patch(plt.Rectangle((.08,y-.055),.84,.1,facecolor='#EAF4F4',edgecolor=teal,lw=2)); ax.text(.11,y+.012,a,weight='bold',color=navy,fontsize=11); ax.text(.11,y-.025,b,color='#334E68',fontsize=9)
 if j<len(boxes)-1: ax.annotate('',(.5,ys[j+1]+.052),(.5,y-.06),arrowprops=dict(arrowstyle='-|>',color=navy))
ax.set_title('LithoTwin - implemented system flow',weight='bold',fontsize=15,color=navy); fig.savefig(OUT/'system_flow.png',dpi=180,bbox_inches='tight'); plt.close(fig)

fig,axs=plt.subplots(1,3,figsize=(10,3.8)); fields=[('edge_distance_px','Edge distance (px)'),('area_error_pct','Area error (%)')]
for ax,(key,title) in zip(axs[:2],fields): ax.bar(['Baseline','AI'],[m['test']['baseline'][key],m['test']['ai'][key]],color=[gold,teal]); ax.set_title(title); ax.bar_label(ax.containers[0],fmt='%.2f')
axs[2].bar(['AI','Reference optics'],[m['test']['ai_us_per_clip'],m['test']['simulator_us_per_clip']],color=[teal,navy]); axs[2].set_title('CPU latency (us/clip)'); axs[2].bar_label(axs[2].containers[0],fmt='%.0f'); fig.suptitle('Held-out engineering metrics',weight='bold',color=navy); plt.tight_layout(); fig.savefig(OUT/'engineering_metrics.png',dpi=180); plt.close(fig)
print(OUT)
