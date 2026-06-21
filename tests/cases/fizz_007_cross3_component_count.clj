;; This test verifies component count propagation through cross3.
;; In Clojure Clisk, (cross3 pos [0.0 1.0 0.0]) returns a 3D vector, whose alpha (4th component) defaults to 1.0.
;; Unmodified C++ code incorrectly returns a 4D vector with alpha equal to 0.0.
(clisk.live/alpha (clisk.live/cross3 clisk.live/pos [0.0 1.0 0.0]))
