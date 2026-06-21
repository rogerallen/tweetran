;; This test verifies the default behavior of the alpha (4th) component selector on a 3D vector.
;; In Clojure Clisk, the alpha component defaults to 1.0f on vectors with fewer than 4 components.
;; Unmodified C++ code incorrectly evaluates this to 0.0f due to get(true) not smearing and 
;; returning the 4th element as 0.0f.
(clisk.live/alpha (clisk.live/vconcat clisk.live/snoise [1.0 2.0]))
