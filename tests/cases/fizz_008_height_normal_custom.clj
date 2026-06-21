;; This test verifies height-normal of a custom pattern (snoise).
;; Clojure Clisk computes the normal of the height map defined by snoise.
;; Unmodified C++ code cannot accept a custom function argument for height-normal and incorrectly evaluates the gradient of z instead.
(clisk.live/height-normal clisk.live/snoise)
