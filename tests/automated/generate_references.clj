(ns generate-references
  (:require [clojure.string :as str])
  (:use [clisk.live])
  (:import [javax.imageio ImageIO]
           [java.io File]))

(defn render-and-save [clj-file png-file]
  (try
    (let [expr (read-string (slurp clj-file))
          pattern (binding [*ns* (find-ns 'clisk.live)]
                    (eval expr))
          img-obj (img pattern 64 64)]
      (ImageIO/write img-obj "png" png-file)
      (println "  ✓ Saved" (.getName png-file)))
    (catch Exception e
      (println "  ✗ Failed rendering" (.getName clj-file) ":" (.getMessage e)))))

(defn -main []
  (let [base-dir (File. (System/getProperty "user.dir"))
        cases-dir (File. base-dir "../cases")
        ref-dir (File. base-dir "../references")]
    (if-not (.exists cases-dir)
      (println "Error: cases directory does not exist at" (.getAbsolutePath cases-dir))
      (do
        (.mkdirs ref-dir)
        (println "Generating references from" (.getAbsolutePath cases-dir) "into" (.getAbsolutePath ref-dir))
        (let [files (filter #(.endsWith (.getName %) ".clj") (.listFiles cases-dir))]
          (doseq [f (sort-by #(.getName %) files)]
            (let [name (.getName f)
                  png-name (str/replace name #"\.clj$" ".png")
                  png-file (File. ref-dir png-name)]
              (println "Processing" name "...")
              (render-and-save f png-file))))))))

(-main)
(shutdown-agents)
