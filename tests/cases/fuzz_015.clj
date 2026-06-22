(rgb-from-hsl (vconcat (lightness-from-rgb (max-component (saturation-from-rgb (vconcat (vconcat (turbulate 0.0915 snoise) (x pos)) [0.5])))) [0.5 0.5]))
