(rgb-from-hsl (v+ [0.0 0.0 0.5] (v+ (dot (vmax (average vturbulence blotches) clouds) (blue-from-hsl (scale 0.4590 splasma))) (sigmoid plasma))))
