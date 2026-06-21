;; This test verifies min-component on a 2D vector with positive components.
;; Clojure Clisk evaluates the minimum component of [0.2 0.3] to be 0.2.
;; Unmodified C++ code incorrectly returns 0.0f because it includes the unassigned 3rd and 4th components (z and w, which are initialized to 0.0f) in the calculation.
(clisk.live/min-component [0.2 0.3])
