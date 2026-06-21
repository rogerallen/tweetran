;; This test verifies component count propagation through lerp.
;; In Clojure Clisk, (lerp 0.5 [1.0 0.5 0.8] 0.0) returns a 3D vector, whose alpha defaults to 1.0.
;; Unmodified C++ code incorrectly returns a 4D vector with alpha equal to 0.0.
(clisk.live/alpha (clisk.live/lerp 0.5 [1.0 0.5 0.8] 0.0))
