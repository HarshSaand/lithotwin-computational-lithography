# LithoTwin - AI-Accelerated Computational Lithography

LithoTwin predicts developed resist contours from a binary mask and process conditions using a compact conditional U-Net trained against a transparent scalar Fourier-optics simulator.

It is an educational process-modeling prototype, not a production lithography, OPC, or chemically amplified resist solver.

## Implemented

- Procedural semiconductor-like mask families: line, line-end, space, elbow, dense lines, two-line gaps, and contacts
- Nine-source scalar Abbe imaging with circular pupils and quadratic defocus phase
- Dose, defocus, numerical-aperture, and resist-threshold conditioning
- Geometry-grouped train/validation/test partitions
- Separate process-range and unseen-contact-family OOD evaluations
- Gaussian imaging baseline and conditional U-Net
- IoU, Dice, symmetric contour distance, area error, Brier score, uncertainty-error correlation, and runtime measurements
- Streamlit workbench, CLI inference, tests, saved checkpoint, and presentation-ready report

## Run on macOS/Linux

```bash
python3 -m venv .venv
source .venv/bin/activate
python -m pip install -r requirements.txt
python scripts/generate_data.py
python scripts/train.py --epochs 12
python scripts/evaluate.py
streamlit run app.py
```

## Run on Windows PowerShell

```powershell
py -3.12 -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install -r requirements.txt
python scripts/generate_data.py
python scripts/train.py --epochs 12 --device cpu
python scripts/evaluate.py
streamlit run app.py
```

## Scientific scope

The dataset is generated locally and contains no claimed experimental fab data. The optical model is coherent and scalar; the threshold-resist model omits partial-coherence integration, polarization, vector effects, flare, aberration calibration, diffusion, and chemical kinetics. Results measure neural fidelity to this declared simulator only.

## Tests

```bash
python -m pytest -q
```
