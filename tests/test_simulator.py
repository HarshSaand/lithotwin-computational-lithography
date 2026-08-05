import numpy as np
from lithotwin.simulator import make_mask,develop,metrics,aerial_image
def test_dose_increases_printed_area():
 m=make_mask('line',np.random.default_rng(1)); _,a=develop(m,.8,0,.65,.35); _,b=develop(m,1.2,0,.65,.35); assert b.sum()>=a.sum()
def test_defocus_changes_aerial_image():
 m=make_mask('elbow',np.random.default_rng(2)); assert not np.allclose(aerial_image(m,1,0,.65),aerial_image(m,1,1,.65))
def test_identity_metrics():
 m=make_mask('contact',np.random.default_rng(3)); q=metrics(m,m); assert q['iou']==1 and q['dice']==1 and q['edge_distance_px']==0
