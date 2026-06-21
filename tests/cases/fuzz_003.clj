(rgb-from-hsl (vconcat (min-component (hsl-from-rgb (t plasma))) (v- (vdivide (length wood) 1.3107) (lerp (vcos blotches) (square vturbulence) (radius clouds)))))
