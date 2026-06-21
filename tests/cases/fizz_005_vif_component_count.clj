;; This test verifies component count propagation through vif.
;; In Clojure Clisk, (vif 1.0 [1.0 0.5 0.8] 0.0) returns a 3D vector, whose alpha (4th component) defaults to 1.0.
;; Unmodified C++ code incorrectly returns a 4D vector [1.0, 0.5, 0.8, 0.0], making its alpha component evaluate to 0.0.
(clisk.live/alpha (clisk.live/vif 1.0 [1.0 0.5 0.8] 0.0))
