;; This test verifies max-component on a 2D vector with negative components, shifted to be in range [0, 1].
;; Clojure Clisk evaluates the maximum component of [-0.2 -0.3] to be -0.2 (plus 1.0 equals 0.8).
;; Unmodified C++ code incorrectly returns 1.0 because it includes the unassigned components (0.0f) in the max calculation, yielding 1.0 + 0.0f = 1.0.
(clisk.live/v+ 1.0 (clisk.live/max-component [-0.2 -0.3]))
