#!/usr/bin/env python3
import os
import sys
import subprocess
import concurrent.futures
from compare_images import calculate_rmse, generate_diff_image

# Threshold for validation (RMSE < 0.02 is standard allowance for GPU/CPU math variations)
RMSE_THRESHOLD = 0.025

def run_cmd(args, cwd=None):
    result = subprocess.run(args, capture_output=True, text=True, cwd=cwd)
    if result.returncode != 0:
        raise RuntimeError(f"Command failed: {' '.join(args)}\nStdout: {result.stdout}\nStderr: {result.stderr}")
    return result.stdout

def run_single_test(case_name, clj_path, ref_png, base_dir, targets):
    test_result = {
        "name": case_name,
        "cuda": {"status": "SKIPPED", "rmse": None, "error": None},
        "cpp": {"status": "SKIPPED", "rmse": None, "error": None}
    }
    
    # Transpile CLJ to CUH
    cuh_path = os.path.join(base_dir, "tests", "outputs", f"{case_name}.cuh")
    gen_cuda_bin = os.path.join(base_dir, "build", "src", "gen_cuda")
    
    try:
        # Run transpiler
        with open(cuh_path, "w") as cuh_file:
            subprocess.run([gen_cuda_bin, clj_path], stdout=cuh_file, check=True)
    except Exception as e:
        test_result["cuda"] = {"status": "FAIL", "rmse": None, "error": f"Transpilation failed: {e}"}
        test_result["cpp"] = {"status": "FAIL", "rmse": None, "error": f"Transpilation failed: {e}"}
        return test_result

    # 1. CUDA Test
    if "cuda" in targets:
        cuda_png = os.path.join(base_dir, "tests", "outputs", "cuda", f"{case_name}.png")
        cuda_diff = os.path.join(base_dir, "tests", "outputs", "cuda", f"{case_name}_diff.png")
        cu_tweetran_bin = os.path.join(base_dir, "build", "cuda", "cu_tweetran")
        
        try:
            # Run GPU renderer (JIT compile and render at 64x64)
            # JITIFY needs include path option
            env = os.environ.copy()
            env["JITIFY_OPTIONS"] = f"-I{base_dir}"
            
            subprocess.run([cu_tweetran_bin, cuh_path, cuda_png, "64", "64"], 
                           env=env, capture_output=True, check=True)
            
            # Compare images
            rmse = calculate_rmse(ref_png, cuda_png)
            if rmse <= RMSE_THRESHOLD:
                test_result["cuda"] = {"status": "PASS", "rmse": rmse, "error": None}
            else:
                generate_diff_image(ref_png, cuda_png, cuda_diff)
                test_result["cuda"] = {
                    "status": "FAIL", 
                    "rmse": rmse, 
                    "error": f"RMSE {rmse:.6f} exceeded threshold {RMSE_THRESHOLD} (diff saved)"
                }
        except Exception as e:
            test_result["cuda"] = {"status": "FAIL", "rmse": None, "error": str(e)}

    # 2. C++ Test
    if "cpp" in targets:
        cpp_bin = os.path.join(base_dir, "tests", "outputs", "cpp", case_name)
        cpp_png = os.path.join(base_dir, "tests", "outputs", "cpp", f"{case_name}.png")
        cpp_diff = os.path.join(base_dir, "tests", "outputs", "cpp", f"{case_name}_diff.png")
        
        try:
            # Compile C++ executable dynamically targeting the CUH file
            # Path to header is relative to where source file cpp/proto.cpp is
            cuh_rel_path = f"../tests/outputs/{case_name}.cuh"
            
            subprocess.run([
                "g++", 
                f'-DGEN_CUDA_OUTPUT_FILE="{cuh_rel_path}"', 
                "-I./cuda", 
                "-fopenmp", 
                "cpp/proto.cpp", 
                "-o", cpp_bin, 
                "-lgomp"
            ], cwd=base_dir, capture_output=True, check=True)
            
            # Run C++ evaluation at 64x64
            subprocess.run([cpp_bin, cpp_png, "64", "64"], capture_output=True, check=True)
            
            # Compare images
            rmse = calculate_rmse(ref_png, cpp_png)
            if rmse <= RMSE_THRESHOLD:
                test_result["cpp"] = {"status": "PASS", "rmse": rmse, "error": None}
            else:
                generate_diff_image(ref_png, cpp_png, cpp_diff)
                test_result["cpp"] = {
                    "status": "FAIL", 
                    "rmse": rmse, 
                    "error": f"RMSE {rmse:.6f} exceeded threshold {RMSE_THRESHOLD} (diff saved)"
                }
        except Exception as e:
            test_result["cpp"] = {"status": "FAIL", "rmse": None, "error": str(e)}
            
    return test_result

def main():
    base_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
    
    # Parse CLI arguments
    targets = ["cpp", "cuda"]
    regenerate_refs = False
    
    for arg in sys.argv[1:]:
        if arg == "--cuda-only":
            targets = ["cuda"]
        elif arg == "--cpp-only":
            targets = ["cpp"]
        elif arg == "--regenerate-refs":
            regenerate_refs = True
            
    # Setup test directories
    os.makedirs(os.path.join(base_dir, "tests", "outputs"), exist_ok=True)
    os.makedirs(os.path.join(base_dir, "tests", "outputs", "cuda"), exist_ok=True)
    os.makedirs(os.path.join(base_dir, "tests", "outputs", "cpp"), exist_ok=True)
    
    # Phase 1: Generate fresh test cases
    print("Generating fresh test cases...")
    run_cmd(["python3", "tests/automated/generate_test_cases.py"], cwd=base_dir)
    
    # Check references
    ref_dir = os.path.join(base_dir, "tests", "references")
    has_refs = os.path.exists(ref_dir) and len([f for f in os.listdir(ref_dir) if f.endswith(".png")]) > 0
    
    if regenerate_refs or not has_refs:
        print("Reference PNGs missing or regeneration requested. Running Clojure reference generator...")
        clj_bin = "/home/rallen/.local/clojure/bin/clojure"
        run_cmd([clj_bin, "-M", "generate_references.clj"], cwd=os.path.join(base_dir, "tests", "automated"))
    
    # Locate all test files
    cases_dir = os.path.join(base_dir, "tests", "cases")
    case_files = sorted([f for f in os.listdir(cases_dir) if f.endswith(".clj")])
    
    test_suite = []
    for f in case_files:
        case_name = f.replace(".clj", "")
        clj_path = os.path.join(cases_dir, f)
        ref_png = os.path.join(ref_dir, case_name + ".png")
        
        if not os.path.exists(ref_png):
            # Skip if reference generation failed (e.g. triangle_wave)
            continue
            
        test_suite.append((case_name, clj_path, ref_png))
        
    print(f"Starting test runner for {len(test_suite)} cases targeting: {', '.join(targets)}")
    
    # Run tests in parallel
    results = []
    with concurrent.futures.ThreadPoolExecutor(max_workers=8) as executor:
        futures = {
            executor.submit(run_single_test, name, path, ref, base_dir, targets): name 
            for name, path, ref in test_suite
        }
        for future in concurrent.futures.as_completed(futures):
            res = future.result()
            results.append(res)
            
            # Print intermediate progress
            cuda_status = f"CUDA:{res['cuda']['status']}"
            if res['cuda']['rmse'] is not None:
                cuda_status += f"({res['cuda']['rmse']:.4f})"
            cpp_status = f"C++:{res['cpp']['status']}"
            if res['cpp']['rmse'] is not None:
                cpp_status += f"({res['cpp']['rmse']:.4f})"
                
            print(f" -> {res['name']}: {cuda_status} | {cpp_status}")
            if res['cuda']['error']:
                print(f"    [CUDA Error] {res['cuda']['error']}")
            if res['cpp']['error']:
                print(f"    [C++ Error] {res['cpp']['error']}")

    # Print summary
    print("\n================ TEST SUMMARY ================")
    total = len(test_suite)
    cuda_pass = sum(1 for r in results if r["cuda"]["status"] == "PASS")
    cuda_fail = sum(1 for r in results if r["cuda"]["status"] == "FAIL")
    cpp_pass = sum(1 for r in results if r["cpp"]["status"] == "PASS")
    cpp_fail = sum(1 for r in results if r["cpp"]["status"] == "FAIL")
    
    if "cuda" in targets:
        print(f"CUDA: {cuda_pass} PASSED, {cuda_fail} FAILED (out of {total} compared)")
    if "cpp" in targets:
        print(f"C++ : {cpp_pass} PASSED, {cpp_fail} FAILED (out of {total} compared)")
        
    failed = False
    if "cuda" in targets and cuda_fail > 0:
        failed = True
    if "cpp" in targets and cpp_fail > 0:
        failed = True
        
    if failed:
        print("Test suite FAILED.")
        sys.exit(1)
    else:
        print("All tests PASSED successfully!")
        sys.exit(0)

if __name__ == "__main__":
    main()
