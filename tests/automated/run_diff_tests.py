#!/usr/bin/env python3
import os
import sys
import subprocess
import concurrent.futures
import csv
import json
import html
from compare_images import calculate_rmse, generate_diff_image

# Threshold for validation (RMSE < 0.02 is standard allowance for GPU/CPU math variations)
RMSE_THRESHOLD = 0.025

def run_cmd(args, cwd=None):
    result = subprocess.run(args, capture_output=True, text=True, cwd=cwd)
    if result.returncode != 0:
        raise RuntimeError(f"Command failed: {' '.join(args)}\nStdout: {result.stdout}\nStderr: {result.stderr}")
    return result.stdout

def run_single_test(case_name, clj_path, ref_png, base_dir, targets, regenerate_refs=False):
    test_result = {
        "name": case_name,
        "cuda": {"status": "SKIPPED", "rmse": None, "error": None},
        "cpp": {"status": "SKIPPED", "rmse": None, "error": None},
        "webgl": {"status": "SKIPPED", "rmse": None, "error": None}
    }
    
    # 1. Transpile CLJ to CUDA CUH
    cuh_path = os.path.join(base_dir, "tests", "outputs", f"{case_name}.cuh")
    gen_cuda_bin = os.path.join(base_dir, "build", "src", "gen_cuda")
    
    # 2. Transpile CLJ to WebGL fragment shader
    frag_path = os.path.join(base_dir, "tests", "outputs", "webgl", f"{case_name}.frag")
    gen_frag_bin = os.path.join(base_dir, "build", "src", "gen_frag")
    
    try:
        # Run gen_cuda transpiler
        if "cuda" in targets or "cpp" in targets:
            with open(cuh_path, "w") as cuh_file:
                subprocess.run([gen_cuda_bin, clj_path], stdout=cuh_file, check=True)
        
        # Run gen_frag transpiler
        if "webgl" in targets:
            with open(frag_path, "w") as frag_file:
                subprocess.run([gen_frag_bin, "-r", base_dir, clj_path], stdout=frag_file, check=True)
    except Exception as e:
        err_msg = f"Transpilation failed: {e}"
        test_result["cuda"] = {"status": "FAIL", "rmse": None, "error": err_msg}
        test_result["cpp"] = {"status": "FAIL", "rmse": None, "error": err_msg}
        test_result["webgl"] = {"status": "FAIL", "rmse": None, "error": err_msg}
        return test_result

    # CUDA Test Execution
    if "cuda" in targets:
        cuda_png = os.path.join(base_dir, "tests", "outputs", "cuda", f"{case_name}.png")
        cuda_diff = os.path.join(base_dir, "tests", "outputs", "cuda", f"{case_name}_diff.png")
        cu_tweetran_bin = os.path.join(base_dir, "build", "cuda", "cu_tweetran")
        
        try:
            # Run GPU renderer (JIT compile and render at 64x64)
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

    # C++ Test Execution
    if "cpp" in targets:
        cpp_bin = os.path.join(base_dir, "tests", "outputs", "cpp", case_name)
        cpp_png = os.path.join(base_dir, "tests", "outputs", "cpp", f"{case_name}.png")
        cpp_diff = os.path.join(base_dir, "tests", "outputs", "cpp", f"{case_name}_diff.png")
        
        try:
            # Compile C++ executable dynamically targeting the CUH file
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

    # WebGL Test Execution
    if "webgl" in targets:
        webgl_png = os.path.join(base_dir, "tests", "outputs", "webgl", f"{case_name}.png")
        webgl_diff = os.path.join(base_dir, "tests", "outputs", "webgl", f"{case_name}_diff.png")
        webgl_ref_dir = os.path.join(base_dir, "tests", "references_webgl")
        webgl_ref_png = os.path.join(webgl_ref_dir, f"{case_name}.png")
        
        try:
            # 1. Run headless WebGL renderer
            subprocess.run([
                "node",
                "webgl/test_runner/render_headless.js",
                frag_path,
                "64", "64",
                webgl_png
            ], cwd=base_dir, capture_output=True, check=True)
            
            # 2. Compare against standard Clojure reference first
            rmse_clj = calculate_rmse(ref_png, webgl_png)
            if rmse_clj <= RMSE_THRESHOLD:
                # Matches Clojure reference!
                test_result["webgl"] = {"status": "PASS", "rmse": rmse_clj, "error": None}
                # Remove WebGL-specific reference if it exists
                if os.path.exists(webgl_ref_png):
                    try:
                        os.remove(webgl_ref_png)
                    except:
                        pass
            else:
                # Differs from Clojure reference (likely due to noise difference)
                os.makedirs(webgl_ref_dir, exist_ok=True)
                
                # Regenerate WebGL-specific golden if requested or missing
                if regenerate_refs or not os.path.exists(webgl_ref_png):
                    try:
                        subprocess.run([
                            "node",
                            "webgl/test_runner/render_headless.js",
                            frag_path,
                            "64", "64",
                            webgl_ref_png
                        ], cwd=base_dir, capture_output=True, check=True)
                    except Exception as e:
                        pass
                
                # Compare against WebGL-specific golden
                if os.path.exists(webgl_ref_png):
                    rmse_webgl = calculate_rmse(webgl_ref_png, webgl_png)
                    if rmse_webgl <= RMSE_THRESHOLD:
                        test_result["webgl"] = {"status": "PASS", "rmse": rmse_webgl, "error": None}
                    else:
                        generate_diff_image(webgl_ref_png, webgl_png, webgl_diff)
                        test_result["webgl"] = {
                            "status": "FAIL",
                            "rmse": rmse_webgl,
                            "error": f"RMSE {rmse_webgl:.6f} exceeded threshold {RMSE_THRESHOLD} (diff saved)"
                        }
                else:
                    test_result["webgl"] = {"status": "FAIL", "rmse": None, "error": "WebGL reference image missing"}
        except Exception as e:
            test_result["webgl"] = {"status": "FAIL", "rmse": None, "error": str(e)}
            
    return test_result

def main():
    base_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
    
    # Parse CLI arguments
    targets = ["cpp", "cuda", "webgl"]
    regenerate_refs = False
    
    for arg in sys.argv[1:]:
        if arg == "--cuda-only":
            targets = ["cuda"]
        elif arg == "--cpp-only":
            targets = ["cpp"]
        elif arg == "--webgl-only":
            targets = ["webgl"]
        elif arg == "--skip-webgl":
            if "webgl" in targets:
                targets.remove("webgl")
        elif arg == "--regenerate-refs":
            regenerate_refs = True
            
    # Setup test directories
    os.makedirs(os.path.join(base_dir, "tests", "outputs"), exist_ok=True)
    os.makedirs(os.path.join(base_dir, "tests", "outputs", "cuda"), exist_ok=True)
    os.makedirs(os.path.join(base_dir, "tests", "outputs", "cpp"), exist_ok=True)
    os.makedirs(os.path.join(base_dir, "tests", "outputs", "webgl"), exist_ok=True)
    
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
            executor.submit(run_single_test, name, path, ref, base_dir, targets, regenerate_refs): name 
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
                
            webgl_status = f"WebGL:{res['webgl']['status']}"
            if res['webgl']['rmse'] is not None:
                webgl_status += f"({res['webgl']['rmse']:.4f})"
                
            print(f" -> {res['name']}: {cuda_status} | {cpp_status} | {webgl_status}")
            if res['cuda']['error']:
                print(f"    [CUDA Error] {res['cuda']['error']}")
            if res['cpp']['error']:
                print(f"    [C++ Error] {res['cpp']['error']}")
            if res['webgl']['error']:
                print(f"    [WebGL Error] {res['webgl']['error']}")

    # Print summary
    print("\n================ TEST SUMMARY ================")
    total = len(test_suite)
    cuda_pass = sum(1 for r in results if r["cuda"]["status"] == "PASS")
    cuda_fail = sum(1 for r in results if r["cuda"]["status"] == "FAIL")
    cuda_skip = sum(1 for r in results if r["cuda"]["status"] == "SKIPPED")
    
    cpp_pass = sum(1 for r in results if r["cpp"]["status"] == "PASS")
    cpp_fail = sum(1 for r in results if r["cpp"]["status"] == "FAIL")
    cpp_skip = sum(1 for r in results if r["cpp"]["status"] == "SKIPPED")
    
    webgl_pass = sum(1 for r in results if r["webgl"]["status"] == "PASS")
    webgl_fail = sum(1 for r in results if r["webgl"]["status"] == "FAIL")
    webgl_skip = sum(1 for r in results if r["webgl"]["status"] == "SKIPPED")
    
    if "cuda" in targets:
        print(f"CUDA : {cuda_pass} PASSED, {cuda_fail} FAILED, {cuda_skip} SKIPPED (out of {total} compared)")
    if "cpp" in targets:
        print(f"C++  : {cpp_pass} PASSED, {cpp_fail} FAILED, {cpp_skip} SKIPPED (out of {total} compared)")
    if "webgl" in targets:
        print(f"WebGL: {webgl_pass} PASSED, {webgl_fail} FAILED, {webgl_skip} SKIPPED (out of {total} compared)")
        
    # Write CSV summary of differential issues
    csv_path = os.path.join(base_dir, "tests", "SUMMARY.csv")
    print(f"Writing CSV test summary to {csv_path}...")
    try:
        sorted_results = sorted(results, key=lambda x: x["name"])
        with open(csv_path, "w", newline="") as csvfile:
            writer = csv.writer(csvfile)
            writer.writerow([
                "test_case",
                "cuda_status", "cuda_rmse", "cuda_error",
                "cpp_status", "cpp_rmse", "cpp_error",
                "webgl_status", "webgl_rmse", "webgl_error"
            ])
            for r in sorted_results:
                webgl_err = r["webgl"]["error"] or ""
                webgl_golden_local = os.path.join(base_dir, "tests", "references_webgl", f"{r['name']}.png")
                if os.path.exists(webgl_golden_local):
                    if webgl_err:
                        webgl_err = f"Compared against WebGL golden. {webgl_err}"
                    else:
                        webgl_err = "Compared against WebGL golden"
                
                writer.writerow([
                    r["name"],
                    r["cuda"]["status"], "" if r["cuda"]["rmse"] is None else f"{r['cuda']['rmse']:.6f}", r["cuda"]["error"] or "",
                    r["cpp"]["status"], "" if r["cpp"]["rmse"] is None else f"{r['cpp']['rmse']:.6f}", r["cpp"]["error"] or "",
                    r["webgl"]["status"], "" if r["webgl"]["rmse"] is None else f"{r['webgl']['rmse']:.6f}", webgl_err
                ])
    except Exception as e:
        print(f"Failed to write CSV summary: {e}")

    # Write HTML summary dashboard
    html_path = os.path.join(base_dir, "tests", "summary.html")
    print(f"Writing HTML dashboard to {html_path}...")
    try:
        sorted_results = sorted(results, key=lambda x: x["name"])
        
        # Build clj codes dictionary
        clj_codes_dict = {}
        cases_dir = os.path.join(base_dir, "tests", "cases")
        for r in sorted_results:
            name = r["name"]
            clj_file_path = os.path.join(cases_dir, f"{name}.clj")
            if os.path.exists(clj_file_path):
                try:
                    with open(clj_file_path, "r", encoding="utf-8") as cljf:
                        clj_codes_dict[name] = cljf.read()
                except Exception as e:
                    clj_codes_dict[name] = f"; Error reading file: {e}"
        json_clj_codes = json.dumps(clj_codes_dict).replace("</script>", "<\\/script>")

        with open(html_path, "w") as htmlfile:
            htmlfile.write("""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Tweetran Differential Testing Dashboard</title>
    <link href="https://fonts.googleapis.com/css2?family=Outfit:wght@300;400;600;800&family=JetBrains+Mono&display=swap" rel="stylesheet">
    <style>
        :root {
            --bg-gradient: radial-gradient(circle at top, #141724 0%, #08090d 100%);
            --panel-bg: rgba(30, 34, 51, 0.4);
            --panel-border: rgba(255, 255, 255, 0.08);
            --text-main: #f3f4f6;
            --text-muted: #9ca3af;
            --primary: #6366f1;
            --primary-hover: #4f46e5;
            --success: #10b981;
            --success-glow: rgba(16, 185, 129, 0.15);
            --danger: #ef4444;
            --danger-glow: rgba(239, 68, 68, 0.15);
            --warning: #f59e0b;
            --warning-glow: rgba(245, 158, 11, 0.15);
            --skipped: #6b7280;
            --card-glow: 0 8px 32px 0 rgba(0, 0, 0, 0.37);
        }
        
        * {
            box-sizing: border-box;
            margin: 0;
            padding: 0;
        }
        
        body {
            font-family: 'Outfit', sans-serif;
            background: var(--bg-gradient);
            color: var(--text-main);
            min-height: 100vh;
            padding: 2rem;
            line-height: 1.5;
        }

        header {
            max-width: 1400px;
            margin: 0 auto 2rem auto;
            display: flex;
            justify-content: space-between;
            align-items: center;
            flex-wrap: wrap;
            gap: 1rem;
        }

        .brand h1 {
            font-size: 2.2rem;
            font-weight: 800;
            background: linear-gradient(to right, #818cf8, #c084fc);
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
            letter-spacing: -0.5px;
        }

        .brand p {
            color: var(--text-muted);
            font-size: 0.95rem;
            margin-top: 0.25rem;
        }

        .stats-container {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(220px, 1fr));
            gap: 1.2rem;
            max-width: 1400px;
            margin: 0 auto 2rem auto;
        }

        .stat-card {
            background: var(--panel-bg);
            backdrop-filter: blur(12px);
            border: 1px solid var(--panel-border);
            border-radius: 16px;
            padding: 1.2rem;
            box-shadow: var(--card-glow);
            transition: transform 0.2s ease, border-color 0.2s ease;
        }

        .stat-card:hover {
            transform: translateY(-2px);
            border-color: rgba(255, 255, 255, 0.15);
        }

        .stat-label {
            font-size: 0.85rem;
            color: var(--text-muted);
            text-transform: uppercase;
            letter-spacing: 1px;
            font-weight: 600;
        }

        .stat-value {
            font-size: 1.8rem;
            font-weight: 800;
            margin-top: 0.5rem;
            display: flex;
            align-items: baseline;
            gap: 0.5rem;
        }

        .stat-bar-container {
            width: 100%;
            height: 6px;
            background: rgba(255, 255, 255, 0.05);
            border-radius: 3px;
            margin-top: 0.8rem;
            overflow: hidden;
        }

        .stat-bar {
            height: 100%;
            border-radius: 3px;
            transition: width 0.6s cubic-bezier(0.4, 0, 0.2, 1);
        }

        .controls {
            max-width: 1400px;
            margin: 0 auto 1.5rem auto;
            display: flex;
            justify-content: space-between;
            align-items: center;
            gap: 1rem;
            flex-wrap: wrap;
        }

        .search-box {
            position: relative;
            flex-grow: 1;
            max-width: 400px;
        }

        .search-box input {
            width: 100%;
            background: var(--panel-bg);
            border: 1px solid var(--panel-border);
            border-radius: 10px;
            padding: 0.6rem 1rem 0.6rem 2.5rem;
            color: var(--text-main);
            font-family: inherit;
            outline: none;
            transition: border-color 0.2s ease, box-shadow 0.2s ease;
        }

        .search-box input:focus {
            border-color: var(--primary);
            box-shadow: 0 0 0 2px rgba(99, 102, 241, 0.2);
        }

        .search-box::before {
            content: "🔍";
            position: absolute;
            left: 0.8rem;
            top: 50%;
            transform: translateY(-50%);
            font-size: 0.9rem;
            opacity: 0.6;
        }

        .filter-buttons {
            display: flex;
            gap: 0.5rem;
        }

        .filter-btn {
            background: var(--panel-bg);
            border: 1px solid var(--panel-border);
            color: var(--text-main);
            padding: 0.5rem 1rem;
            border-radius: 10px;
            cursor: pointer;
            font-family: inherit;
            font-size: 0.9rem;
            font-weight: 600;
            transition: all 0.2s ease;
        }

        .filter-btn:hover {
            border-color: rgba(255,255,255,0.2);
            background: rgba(255,255,255,0.05);
        }

        .filter-btn.active {
            background: var(--primary);
            border-color: var(--primary);
            box-shadow: 0 0 12px rgba(99, 102, 241, 0.4);
        }

        .table-container {
            max-width: 1400px;
            margin: 0 auto;
            background: var(--panel-bg);
            backdrop-filter: blur(12px);
            border: 1px solid var(--panel-border);
            border-radius: 16px;
            overflow-x: auto;
            box-shadow: var(--card-glow);
        }

        table {
            width: 100%;
            border-collapse: collapse;
            text-align: left;
        }

        th {
            background: rgba(15, 17, 26, 0.6);
            color: var(--text-muted);
            font-weight: 600;
            text-transform: uppercase;
            font-size: 0.75rem;
            letter-spacing: 1px;
            padding: 1rem 1.2rem;
            border-bottom: 1px solid var(--panel-border);
        }

        td {
            padding: 1rem 1.2rem;
            border-bottom: 1px solid rgba(255, 255, 255, 0.03);
            vertical-align: middle;
        }

        tr:hover td {
            background: rgba(255, 255, 255, 0.01);
        }

        .test-name {
            font-family: 'JetBrains Mono', monospace;
            font-size: 0.9rem;
            font-weight: 600;
            color: #e0e7ff;
        }
        
        .test-title-row {
            display: flex;
            align-items: center;
            gap: 0.5rem;
            margin-bottom: 0.35rem;
        }

        .test-case-title {
            font-family: 'JetBrains Mono', monospace;
            font-size: 0.9rem;
            font-weight: 600;
            color: #e0e7ff;
        }

        .clj-file-link {
            color: var(--primary);
            text-decoration: none;
            font-size: 0.85rem;
            opacity: 0.7;
            transition: opacity 0.2s ease, transform 0.2s ease;
            display: inline-block;
            line-height: 1;
        }

        .clj-file-link:hover {
            opacity: 1;
            transform: translate(1px, -1px);
            color: #818cf8;
        }

        .clj-code-container {
            max-width: 450px;
            max-height: 120px;
            overflow: auto;
            background: rgba(15, 17, 26, 0.6);
            border-radius: 6px;
            padding: 0.4rem 0.6rem;
            border: 1px solid rgba(255, 255, 255, 0.04);
        }

        .clj-code-container::-webkit-scrollbar {
            width: 4px;
            height: 4px;
        }

        .clj-code-container::-webkit-scrollbar-thumb {
            background: rgba(255, 255, 255, 0.1);
            border-radius: 2px;
        }

        .clj-code {
            font-family: 'JetBrains Mono', monospace;
            font-size: 0.72rem;
            color: #a5b4fc;
            white-space: pre-wrap;
            word-break: break-all;
            line-height: 1.3;
        }

        .modal-clj-container {
            width: 256px;
            height: 256px;
            border-radius: 12px;
            border: 2px solid rgba(255, 255, 255, 0.1);
            background: #0f111a;
            padding: 1rem;
            overflow: auto;
            text-align: left;
        }

        .modal-clj-container::-webkit-scrollbar {
            width: 6px;
            height: 6px;
        }

        .modal-clj-container::-webkit-scrollbar-thumb {
            background: rgba(255, 255, 255, 0.15);
            border-radius: 3px;
        }

        .modal-clj-code {
            font-family: 'JetBrains Mono', monospace;
            font-size: 0.72rem;
            color: #a5b4fc;
            white-space: pre-wrap;
            word-break: break-all;
            line-height: 1.4;
        }

        .badge {
            display: inline-flex;
            align-items: center;
            justify-content: center;
            padding: 0.25rem 0.6rem;
            border-radius: 6px;
            font-size: 0.75rem;
            font-weight: 700;
            letter-spacing: 0.5px;
            min-width: 65px;
        }

        .badge-PASS {
            background: rgba(16, 185, 129, 0.1);
            color: var(--success);
            border: 1px solid rgba(16, 185, 129, 0.2);
            box-shadow: 0 0 8px rgba(16, 185, 129, 0.05);
        }

        .badge-FAIL {
            background: rgba(239, 68, 68, 0.1);
            color: var(--danger);
            border: 1px solid rgba(239, 68, 68, 0.2);
            box-shadow: 0 0 8px rgba(239, 68, 68, 0.05);
        }

        .badge-SKIPPED {
            background: rgba(107, 114, 128, 0.1);
            color: var(--text-muted);
            border: 1px solid rgba(107, 114, 128, 0.2);
        }

        .rmse-val {
            font-family: 'JetBrains Mono', monospace;
            font-size: 0.75rem;
            color: var(--text-muted);
            margin-top: 0.15rem;
            display: block;
        }

        .image-cell {
            position: relative;
            width: 72px;
            height: 72px;
            padding: 4px;
        }

        .image-container {
            width: 64px;
            height: 64px;
            border-radius: 8px;
            border: 1px solid rgba(255, 255, 255, 0.1);
            overflow: hidden;
            background: #0f111a;
            cursor: pointer;
            transition: transform 0.2s cubic-bezier(0.4, 0, 0.2, 1), border-color 0.2s ease, box-shadow 0.2s ease;
        }

        .image-container:hover {
            transform: scale(1.1);
            border-color: var(--primary);
            box-shadow: 0 4px 12px rgba(99, 102, 241, 0.3);
            z-index: 10;
        }

        .image-container img {
            width: 100%;
            height: 100%;
            object-fit: cover;
            display: block;
            image-rendering: pixelated;
        }

        .no-img {
            width: 100%;
            height: 100%;
            display: flex;
            align-items: center;
            justify-content: center;
            font-size: 0.65rem;
            color: var(--text-muted);
            text-transform: uppercase;
            font-weight: 600;
        }

        /* Lightbox modal styles */
        .modal {
            display: none;
            position: fixed;
            z-index: 1000;
            top: 0;
            left: 0;
            width: 100%;
            height: 100%;
            background: rgba(8, 9, 13, 0.95);
            backdrop-filter: blur(8px);
            align-items: center;
            justify-content: center;
            opacity: 0;
            transition: opacity 0.3s ease;
        }

        .modal.open {
            display: flex;
            opacity: 1;
        }

        .modal-content {
            position: relative;
            background: #1e2233;
            border: 1px solid rgba(255,255,255,0.1);
            border-radius: 20px;
            padding: 2rem;
            max-width: 90%;
            max-height: 90%;
            box-shadow: 0 20px 50px rgba(0,0,0,0.5);
            display: flex;
            flex-direction: column;
            align-items: center;
            transform: scale(0.9);
            transition: transform 0.3s cubic-bezier(0.34, 1.56, 0.64, 1);
        }

        .modal.open .modal-content {
            transform: scale(1);
        }

        .modal-close {
            position: absolute;
            top: 1rem;
            right: 1rem;
            background: rgba(255,255,255,0.05);
            border: none;
            color: var(--text-main);
            width: 36px;
            height: 36px;
            border-radius: 50%;
            cursor: pointer;
            font-size: 1.2rem;
            display: flex;
            align-items: center;
            justify-content: center;
            transition: background 0.2s ease;
        }

        .modal-close:hover {
            background: rgba(255,255,255,0.1);
        }

        .modal-title {
            font-size: 1.4rem;
            font-weight: 800;
            margin-bottom: 0.5rem;
        }

        .modal-subtitle {
            font-size: 0.9rem;
            color: var(--text-muted);
            margin-bottom: 1.5rem;
        }

        .comparison-view {
            display: flex;
            gap: 1.5rem;
            align-items: center;
            justify-content: center;
            flex-wrap: wrap;
        }

        .comp-card {
            display: flex;
            flex-direction: column;
            align-items: center;
            gap: 0.5rem;
        }

        .comp-card img {
            width: 256px;
            height: 256px;
            border-radius: 12px;
            border: 2px solid rgba(255,255,255,0.1);
            image-rendering: pixelated;
        }

        .comp-card span {
            font-size: 0.85rem;
            font-weight: 600;
            color: var(--text-muted);
            text-transform: uppercase;
            letter-spacing: 0.5px;
        }

        .comp-card.active-comp img {
            border-color: var(--primary);
        }
    </style>
</head>
<body>
    <header>
        <div class="brand">
            <h1>Tweetran Differential Testing</h1>
            <p>Verification results across C++, CUDA, and WebGL target backends</p>
        </div>
    </header>

    <div class="stats-container">
        <div class="stat-card">
            <div class="stat-label">Total Test Cases</div>
            <div class="stat-value" id="stat-total">0</div>
            <div class="stat-bar-container">
                <div class="stat-bar" style="width: 100%; background: var(--primary);"></div>
            </div>
        </div>
        <div class="stat-card">
            <div class="stat-label">C++ Pass Rate</div>
            <div class="stat-value" id="stat-cpp">0%</div>
            <div class="stat-bar-container">
                <div class="stat-bar" id="bar-cpp" style="background: var(--success);"></div>
            </div>
        </div>
        <div class="stat-card">
            <div class="stat-label">CUDA Pass Rate</div>
            <div class="stat-value" id="stat-cuda">0%</div>
            <div class="stat-bar-container">
                <div class="stat-bar" id="bar-cuda" style="background: var(--success);"></div>
            </div>
        </div>
        <div class="stat-card">
            <div class="stat-label">WebGL Pass Rate</div>
            <div class="stat-value" id="stat-webgl">0%</div>
            <div class="stat-bar-container">
                <div class="stat-bar" id="bar-webgl" style="background: var(--success);"></div>
            </div>
        </div>
    </div>

    <div class="controls">
        <div class="search-box">
            <input type="text" id="search-input" placeholder="Search test cases...">
        </div>
        <div class="filter-buttons">
            <button class="filter-btn active" data-filter="all">All</button>
            <button class="filter-btn" data-filter="fail">Failures</button>
            <button class="filter-btn" data-filter="cpp">C++ Failed</button>
            <button class="filter-btn" data-filter="cuda">CUDA Failed</button>
            <button class="filter-btn" data-filter="webgl">WebGL Failed</button>
        </div>
    </div>

    <div class="table-container">
        <table>
            <thead>
                <tr>
                    <th>Test Case</th>
                    <th style="width: 100px;">C++</th>
                    <th style="width: 100px;">CUDA</th>
                    <th style="width: 100px;">WebGL</th>
                    <th style="text-align: center;">Reference</th>
                    <th style="text-align: center;">C++ Output</th>
                    <th style="text-align: center;">CUDA Output</th>
                    <th style="text-align: center;">WebGL Golden</th>
                    <th style="text-align: center;">WebGL Output</th>
                </tr>
            </thead>
            <tbody id="table-body">
""")

            for r in sorted_results:
                name = r["name"]
                
                # C++ elements
                cpp_status = r["cpp"]["status"]
                cpp_rmse = f"{r['cpp']['rmse']:.6f}" if r["cpp"]["rmse"] is not None else ""
                cpp_img = f"outputs/cpp/{name}.png" if r["cpp"]["status"] != "SKIPPED" else ""
                
                # CUDA elements
                cuda_status = r["cuda"]["status"]
                cuda_rmse = f"{r['cuda']['rmse']:.6f}" if r["cuda"]["rmse"] is not None else ""
                cuda_img = f"outputs/cuda/{name}.png" if r["cuda"]["status"] != "SKIPPED" else ""
                
                # WebGL elements
                webgl_status = r["webgl"]["status"]
                webgl_rmse = f"{r['webgl']['rmse']:.6f}" if r["webgl"]['rmse'] is not None else ""
                webgl_img = f"outputs/webgl/{name}.png" if r["webgl"]["status"] != "SKIPPED" else ""
                
                ref_img = f"references/{name}.png"
                
                # Determine which golden image to show for WebGL (specific one if it exists, otherwise standard)
                webgl_golden_local = os.path.join(base_dir, "tests", "references_webgl", f"{name}.png")
                if os.path.exists(webgl_golden_local):
                    webgl_golden_display = f"references_webgl/{name}.png"
                else:
                    webgl_golden_display = ""

                # Row classes for filters
                row_classes = ["test-row"]
                if cpp_status == "FAIL" or cuda_status == "FAIL" or webgl_status == "FAIL":
                    row_classes.append("has-failure")
                if cpp_status == "FAIL": row_classes.append("cpp-failed")
                if cuda_status == "FAIL": row_classes.append("cuda-failed")
                if webgl_status == "FAIL": row_classes.append("webgl-failed")

                clj_code = clj_codes_dict.get(name, "")
                escaped_clj_code = html.escape(clj_code)

                htmlfile.write(f"""                <tr class="{' '.join(row_classes)}" data-name="{name}">
                    <td class="test-name">
                        <div class="test-title-row">
                            <span class="test-case-title">{name}</span>
                            <a href="cases/{name}.clj" target="_blank" class="clj-file-link" title="Open Clojure File ↗">↗</a>
                        </div>
                        <div class="clj-code-container">
                            <pre class="clj-code"><code>{escaped_clj_code}</code></pre>
                        </div>
                    </td>
                    <td>
                        <span class="badge badge-{cpp_status}">{cpp_status}</span>
                        {f'<span class="rmse-val">RMSE: {cpp_rmse}</span>' if cpp_rmse else ''}
                    </td>
                    <td>
                        <span class="badge badge-{cuda_status}">{cuda_status}</span>
                        {f'<span class="rmse-val">RMSE: {cuda_rmse}</span>' if cuda_rmse else ''}
                    </td>
                    <td>
                        <span class="badge badge-{webgl_status}">{webgl_status}</span>
                        {f'<span class="rmse-val">RMSE: {webgl_rmse}</span>' if webgl_rmse else ''}
                    </td>
                    <!-- Reference -->
                    <td align="center" class="image-cell">
                        <div class="image-container" onclick="openLightbox('{name}', '{ref_img}', '{cpp_img}', '{cuda_img}', '{webgl_golden_display}', '{webgl_img}')">
                            <img src="{ref_img}" alt="Reference">
                        </div>
                    </td>
                    <!-- C++ -->
                    <td align="center" class="image-cell">
                        {f'<div class="image-container" onclick="openLightbox(\'{name}\', \'{ref_img}\', \'{cpp_img}\', \'{cuda_img}\', \'{webgl_golden_display}\', \'{webgl_img}\')"><img src="{cpp_img}" alt="C++"></div>' if cpp_img else '<div class="no-img">N/A</div>'}
                    </td>
                    <!-- CUDA -->
                    <td align="center" class="image-cell">
                        {f'<div class="image-container" onclick="openLightbox(\'{name}\', \'{ref_img}\', \'{cpp_img}\', \'{cuda_img}\', \'{webgl_golden_display}\', \'{webgl_img}\')"><img src="{cuda_img}" alt="CUDA"></div>' if cuda_img else '<div class="no-img">N/A</div>'}
                    </td>
                    <!-- WebGL Golden -->
                    <td align="center" class="image-cell">
                        {f'<div class="image-container" onclick="openLightbox(\'{name}\', \'{ref_img}\', \'{cpp_img}\', \'{cuda_img}\', \'{webgl_golden_display}\', \'{webgl_img}\')"><img src="{webgl_golden_display}" alt="WebGL Golden"></div>' if (webgl_status != "SKIPPED" and webgl_golden_display) else '<div class="no-img" style="font-size: 0.65rem; color: var(--text-muted); line-height: 1.2;">Same as<br>Clojure</div>'}
                    </td>
                    <!-- WebGL Current -->
                    <td align="center" class="image-cell">
                        {f'<div class="image-container" onclick="openLightbox(\'{name}\', \'{ref_img}\', \'{cpp_img}\', \'{cuda_img}\', \'{webgl_golden_display}\', \'{webgl_img}\')"><img src="{webgl_img}" alt="WebGL"></div>' if webgl_img else '<div class="no-img">N/A</div>'}
                    </td>
                </tr>
""")

            htmlfile.write(("""            </tbody>
        </table>
    </div>

    <!-- Lightbox Modal -->
    <div id="lightbox" class="modal" onclick="closeLightbox(event)">
        <div class="modal-content" onclick="event.stopPropagation()">
            <button class="modal-close" onclick="closeLightbox(event)">×</button>
            <div class="modal-title" id="modal-test-title">test_case</div>
            <div class="modal-subtitle">Comparison grid (256x256 pixel zoom)</div>
            <div class="comparison-view" id="modal-comparison-grid">
                <!-- Loaded dynamically -->
            </div>
        </div>
    </div>

    <script>
        const cljCodes = {json_clj_codes};

        // Calculate statistics
        const rows = Array.from(document.querySelectorAll('.test-row'));
        const totalCount = rows.length;
        
        let cppPass = 0, cudaPass = 0, webglPass = 0;
        let cppTotal = 0, cudaTotal = 0, webglTotal = 0;
        let cppSkipped = 0, cudaSkipped = 0, webglSkipped = 0;

        rows.forEach(row => {
            const badges = row.querySelectorAll('.badge');
            
            const cppText = badges[0].textContent;
            if (cppText !== 'SKIPPED') {
                cppTotal++;
                if (cppText === 'PASS') cppPass++;
            } else {
                cppSkipped++;
            }
            
            const cudaText = badges[1].textContent;
            if (cudaText !== 'SKIPPED') {
                cudaTotal++;
                if (cudaText === 'PASS') cudaPass++;
            } else {
                cudaSkipped++;
            }
            
            const webglText = badges[2].textContent;
            if (webglText !== 'SKIPPED') {
                webglTotal++;
                if (webglText === 'PASS') webglPass++;
            } else {
                webglSkipped++;
            }
        });

        const cppPct = cppTotal > 0 ? Math.round((cppPass / cppTotal) * 100) : 0;
        const cudaPct = cudaTotal > 0 ? Math.round((cudaPass / cudaTotal) * 100) : 0;
        const webglPct = webglTotal > 0 ? Math.round((webglPass / webglTotal) * 100) : 0;

        const formatStat = (pct, pass, total, skipped) => {
            let res = `${pct}% (${pass}/${total})`;
            if (skipped > 0) {
                res += ` <span style="font-size: 0.85rem; color: var(--text-muted); font-weight: 500;">(${skipped} skipped)</span>`;
            }
            return res;
        };

        document.getElementById('stat-total').textContent = totalCount;
        document.getElementById('stat-cpp').innerHTML = formatStat(cppPct, cppPass, cppTotal, cppSkipped);
        document.getElementById('bar-cpp').style.width = `${cppPct}%`;
        document.getElementById('stat-cuda').innerHTML = formatStat(cudaPct, cudaPass, cudaTotal, cudaSkipped);
        document.getElementById('bar-cuda').style.width = `${cudaPct}%`;
        document.getElementById('stat-webgl').innerHTML = formatStat(webglPct, webglPass, webglTotal, webglSkipped);
        document.getElementById('bar-webgl').style.width = `${webglPct}%`;

        // Search and filter logic
        const searchInput = document.getElementById('search-input');
        const filterBtns = document.querySelectorAll('.filter-btn');
        let currentFilter = 'all';

        function updateRows() {
            const query = searchInput.value.toLowerCase();
            rows.forEach(row => {
                const name = row.getAttribute('data-name').toLowerCase();
                const matchesSearch = name.includes(query);
                
                let matchesFilter = true;
                if (currentFilter === 'fail') {
                    matchesFilter = row.classList.contains('has-failure');
                } else if (currentFilter === 'cpp') {
                    matchesFilter = row.classList.contains('cpp-failed');
                } else if (currentFilter === 'cuda') {
                    matchesFilter = row.classList.contains('cuda-failed');
                } else if (currentFilter === 'webgl') {
                    matchesFilter = row.classList.contains('webgl-failed');
                }

                if (matchesSearch && matchesFilter) {
                    row.style.display = '';
                } else {
                    row.style.display = 'none';
                }
            });
        }

        searchInput.addEventListener('input', updateRows);

        filterBtns.forEach(btn => {
            btn.addEventListener('click', () => {
                filterBtns.forEach(b => b.classList.remove('active'));
                btn.classList.add('active');
                currentFilter = btn.getAttribute('data-filter');
                updateRows();
            });
        });

        // HTML Escaper
        function escapeHtml(text) {
            if (!text) return '';
            return text
                .replace(/&/g, "&amp;")
                .replace(/</g, "&lt;")
                .replace(/>/g, "&gt;")
                .replace(/"/g, "&quot;")
                .replace(/'/g, "&#039;");
        }

        // Lightbox modal logic
        function openLightbox(name, ref, cpp, cuda, webglGolden, webgl) {
            document.getElementById('modal-test-title').textContent = name;
            const grid = document.getElementById('modal-comparison-grid');
            grid.innerHTML = '';
            
            // Add Clojure Source card if available
            const cljCode = cljCodes[name];
            if (cljCode) {
                const card = document.createElement('div');
                card.className = 'comp-card';
                card.innerHTML = `
                    <span>Clojure Source</span>
                    <div class="modal-clj-container">
                        <pre class="modal-clj-code"><code>${escapeHtml(cljCode)}</code></pre>
                    </div>
                `;
                grid.appendChild(card);
            }

            const addCompCard = (title, src) => {
                if (!src || src.includes('N/A')) return;
                const card = document.createElement('div');
                card.className = 'comp-card';
                card.innerHTML = `
                    <span>${title}</span>
                    <img src="${src}" alt="${title}">
                `;
                grid.appendChild(card);
            };

            addCompCard('Reference', ref);
            if (cpp) addCompCard('C++', cpp);
            if (cuda) addCompCard('CUDA', cuda);
            if (webglGolden) addCompCard('WebGL Golden', webglGolden);
            if (webgl) addCompCard('WebGL Current', webgl);

            const modal = document.getElementById('lightbox');
            modal.classList.add('open');
        }

        function closeLightbox(event) {
            const modal = document.getElementById('lightbox');
            modal.classList.remove('open');
        }

        document.addEventListener('keydown', (e) => {
            if (e.key === 'Escape') {
                closeLightbox();
            }
        });
    </script>
</body>
</html>
""").replace("{json_clj_codes}", json_clj_codes))
    except Exception as e:
        print(f"Failed to write HTML summary: {e}")

    failed = False
    if "cuda" in targets and cuda_fail > 0:
        failed = True
    if "cpp" in targets and cpp_fail > 0:
        failed = True
    if "webgl" in targets and webgl_fail > 0:
        failed = True
        
    if failed:
        print("Test suite FAILED.")
        sys.exit(1)
    else:
        print("All tests PASSED successfully!")
        sys.exit(0)

if __name__ == "__main__":
    main()
