from pathlib import Path
import sys
import numpy as np,torch,streamlit as st,matplotlib.pyplot as plt
ROOT=Path(__file__).resolve().parent; sys.path.insert(0,str(ROOT/'src'))
from lithotwin.simulator import make_mask,develop,metrics
from lithotwin.data import channels
from lithotwin.model import ConditionalUNet
st.set_page_config(page_title='LithoTwin',layout='wide'); st.title('LithoTwin - AI Computational Lithography Workbench'); st.caption('Reduced-order scalar optics and neural surrogate. Not a production lithography or resist solver.')
family=st.sidebar.selectbox('Mask family',['line','line_end','space','elbow','dense','two_line','contact']); seed=st.sidebar.number_input('Geometry seed',0,999,12); dose=st.sidebar.slider('Relative dose',.65,1.35,1.0,.01); focus=st.sidebar.slider('Defocus',-2.0,2.0,0.0,.05); na=st.sidebar.slider('Numerical aperture',.55,.75,.65,.01); threshold=st.sidebar.slider('Resist threshold',.20,.55,.35,.01)
mask=make_mask(family,np.random.default_rng(int(seed))); aerial,ref=develop(mask,dose,focus,na,threshold); ckpath=ROOT/'artifacts/lithotwin.pt'
if not ckpath.exists(): st.error('Run data generation and training first.'); st.stop()
ck=torch.load(ckpath,map_location='cpu',weights_only=False); model=ConditionalUNet(**ck['config']); model.load_state_dict(ck['state_dict']); model.eval(); p=np.array([[dose,focus,na,threshold]],np.float32)
with torch.no_grad(): prob=torch.sigmoid(model(torch.from_numpy(channels(mask[None],p)))).numpy()[0,0]
pred=prob>=.5; q=metrics(ref,pred); c1,c2,c3,c4=st.columns(4); c1.metric('IoU',f"{q['iou']:.3f}"); c2.metric('Dice',f"{q['dice']:.3f}"); c3.metric('Edge distance',f"{q['edge_distance_px']:.2f} px"); c4.metric('Area error',f"{q['area_error_pct']:.1f}%")
if family=='contact' or abs(focus)>1.15 or not (.78<=dose<=1.22): st.warning('OOD condition: use the physics simulation as the authority.')
fig,axs=plt.subplots(1,5,figsize=(14,3)); items=[(mask,'Mask'),(aerial,'Aerial image'),(ref,'Physics resist'),(prob,'AI probability'),(pred.astype(float)-ref,'Signed error')]
for ax,(im,title) in zip(axs,items): ax.imshow(im,cmap='coolwarm' if title=='Signed error' else 'viridis',vmin=-1 if title=='Signed error' else None,vmax=1 if title=='Signed error' else None); ax.set_title(title); ax.axis('off')
plt.tight_layout(); st.pyplot(fig)
st.write('Process parameters',{'dose':dose,'defocus':focus,'NA':na,'threshold':threshold,'family':family})
