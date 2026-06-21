(rgb-from-hsl (vmin (hue-from-rgb (hue-from-rgb (vsqrt vnoise))) (v* (lerp (vfrac agate) (dot clouds wood) (scale 3.4404 splasma)) (vpow (clamp pos -0.5652 0.9074) [1.8876 1.0478 0.0307]))))
