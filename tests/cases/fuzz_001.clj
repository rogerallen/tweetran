(rgb-from-hsl (v+ [0.0 0.0 0.4] (vmin (vconcat (hue-from-rgb (vconcat (vconcat (x pos) (y pos)) [0.2])) [0.5 0.5]) spots)))
