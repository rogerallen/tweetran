;; This test verifies the vlength reduction behavior on a 1D scalar.
;; In Clojure Clisk, (length scalar) equals the absolute value |scalar| (a 1D magnitude).
;; Unmodified C++ code incorrectly smears the scalar to 4D [v, v, v, v] before computing length,
;; resulting in 2.0 * |scalar| (an incorrect scaling factor of 2.0).
(clisk.live/length clisk.live/snoise)
