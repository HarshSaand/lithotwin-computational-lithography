# Data provenance and scientific scope

The complete dataset in `data/lithography.npz` is generated locally by `scripts/generate_data.py` with seed 42. It contains no proprietary masks, experimental wafer measurements, or third-party layout files.

Ground truth is produced by the declared reduced-order simulator in `src/lithotwin/simulator.py`: nine shifted scalar source points, circular pupils, a quadratic defocus phase, incoherent source-intensity averaging, relative dose scaling, and threshold resist development.

The equations are motivated by standard Fourier-optics and computational-lithography treatments, including:

- J. W. Goodman, *Introduction to Fourier Optics*, 3rd ed.
- A. K. Wong, *Resolution Enhancement Techniques in Optical Lithography*.
- C. A. Mack, *Fundamental Principles of Optical Lithography*.

The generated evidence validates software and surrogate fidelity to this model only. It is not calibrated to a scanner, resist stack, mask process, or A*STAR IME fabrication line.
