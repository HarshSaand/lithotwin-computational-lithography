"""Transparent scalar Fourier-optics lithography simulator.

This educational model uses coherent scalar imaging and threshold resist
development. It is intentionally not a production Hopkins/Abbe resist solver.
"""
from __future__ import annotations
import numpy as np
from scipy import ndimage

GRID = 48

def make_mask(family: str, rng: np.random.Generator, n: int = GRID) -> np.ndarray:
    """Create a binary Manhattan mask clip with reproducible random geometry."""
    m=np.zeros((n,n),np.float32); yy,xx=np.mgrid[:n,:n]; w=int(rng.integers(4,11)); cx=int(rng.integers(17,32)); cy=int(rng.integers(17,32))
    if family=="line": m[:,max(0,cx-w//2):min(n,cx+(w+1)//2)]=1
    elif family=="line_end": m[5:cy+8,max(0,cx-w//2):min(n,cx+(w+1)//2)]=1
    elif family=="space": m[:]=1; m[:,max(0,cx-w//2):min(n,cx+(w+1)//2)]=0
    elif family=="elbow": m[cy-w//2:cy+w//2,6:cx+w//2]=1; m[cy-w//2:n-5,cx-w//2:cx+w//2]=1
    elif family=="dense":
        pitch=int(rng.integers(8,15)); width=max(3,pitch//2)
        for x in range(int(rng.integers(0,pitch)),n,pitch): m[:,x:min(n,x+width)]=1
    elif family=="contact":
        r=float(rng.uniform(3.0,7.0)); m[((xx-cx)**2+(yy-cy)**2)<=r*r]=1
    elif family=="two_line":
        gap=int(rng.integers(3,10)); x0=cx-w-gap//2; m[:,max(0,x0-w):max(0,x0)]=1; x1=cx+gap//2; m[:,x1:min(n,x1+w)]=1
    else: raise ValueError(f"unknown family {family}")
    return m

def aerial_image(mask: np.ndarray, dose: float=1.0, defocus: float=0.0, na: float=0.65) -> np.ndarray:
    """Nine-source scalar Abbe approximation with defocused circular pupils."""
    n=mask.shape[0]; fy=np.fft.fftfreq(n); fx=np.fft.fftfreq(n); ky,kx=np.meshgrid(fy,fx,indexing='ij'); cutoff=.12*(na/.65); spectrum=np.fft.fft2(mask); intensity=0.0
    # A small source grid approximates partial coherence and makes the reference
    # physics meaningfully more expensive than a single blur/threshold pass.
    shifts=(-.035,0.0,.035)
    for sy in shifts:
        for sx in shifts:
            kr=np.sqrt((kx-sx)**2+(ky-sy)**2); pupil=(kr<=cutoff).astype(np.complex64); phase=np.exp(1j*np.pi*defocus*(kr/max(cutoff,1e-6))**2); field=np.fft.ifft2(spectrum*pupil*phase); intensity += np.abs(field)**2/9.0
    return (dose*intensity).astype(np.float32)

def develop(mask: np.ndarray, dose: float, defocus: float, na: float, threshold: float) -> tuple[np.ndarray,np.ndarray]:
    aerial=aerial_image(mask,dose,defocus,na); resist=(aerial>=threshold).astype(np.float32); return aerial,resist

def gaussian_baseline(mask: np.ndarray,dose: float,defocus:float,threshold:float) -> np.ndarray:
    sigma=1.5+1.2*abs(defocus); image=ndimage.gaussian_filter(mask.astype(float),sigma=sigma)*dose; return (image>=threshold).astype(np.float32)

def edge_distance(reference: np.ndarray,prediction: np.ndarray) -> float:
    er_ref=reference.astype(bool)^ndimage.binary_erosion(reference.astype(bool)); er_pred=prediction.astype(bool)^ndimage.binary_erosion(prediction.astype(bool))
    if not er_ref.any() or not er_pred.any(): return float(GRID)
    d1=ndimage.distance_transform_edt(~er_ref)[er_pred].mean(); d2=ndimage.distance_transform_edt(~er_pred)[er_ref].mean(); return float((d1+d2)/2)

def metrics(reference: np.ndarray,prediction: np.ndarray) -> dict[str,float]:
    r=reference>0.5; p=prediction>0.5; inter=np.logical_and(r,p).sum(); union=np.logical_or(r,p).sum(); area_r=max(r.sum(),1)
    return {"iou":float(inter/max(union,1)),"dice":float(2*inter/max(r.sum()+p.sum(),1)),"edge_distance_px":edge_distance(r,p),"area_error_pct":float(abs(p.sum()-r.sum())/area_r*100)}
