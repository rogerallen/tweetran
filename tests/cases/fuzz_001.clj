(rgb-from-hsl (vmin (saturation-from-rgb (dot (hue-from-rgb noise) (lerp vturbulence vplasma vturbulence))) spots))
