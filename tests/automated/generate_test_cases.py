#!/usr/bin/env python3
import os
import sys

def main():
    # Setup directories
    base_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
    cases_dir = os.path.join(base_dir, "tests", "cases")
    os.makedirs(cases_dir, exist_ok=True)
    
    # Function categories (from gen_expressions.py)
    term_fns = [
        "noise", "snoise", "plasma", "splasma", "vnoise", "vsnoise", "vplasma", "vsplasma",
        "grain", "turbulence", "vturbulence", "spots", "blotches", "agate", "clouds", "velvet", "flecks", "wood"
    ]
    
    unary_fns = [
        "vsin", "vcos", "vabs", "vround", "vfloor", "vfrac", "square", "vsqrt", "sigmoid", "triangle-wave",
        "max-component", "min-component", "length", "normalize", "gradient", "theta", "radius", "polar",
        "height", "height-normal", "hue-from-rgb", "lightness-from-rgb", "saturation-from-rgb", "hsl-from-rgb",
        "red-from-hsl", "green-from-hsl", "blue-from-hsl", "rgb-from-hsl", "x", "y", "z", "t", "alpha"
    ]
    
    binary_fns = [
        "v+", "v*", "v-", "vdivide", "vpow", "vmod", "dot", "cross3", "vmin", "vmax",
        "turbulate", "checker", "rotate", "scale", "offset", "adjust-hue", "adjust-hsl", "vconcat", "average"
    ]
    
    ternary_fns = [
        "lerp", "clamp", "vif"
    ]
    
    # Custom templates for functions with specific arguments requirements
    custom_templates = {
        # Modpos binary/unary functions (require a function/pattern as parameter)
        "scale": "(clisk.live/scale 0.5 (clisk.live/x clisk.live/pos))",
        "offset": "(clisk.live/offset [0.5 0.5 0.5 0.5] (clisk.live/x clisk.live/pos))",
        "rotate": "(clisk.live/rotate 0.78 (clisk.live/x clisk.live/pos))",
        "turbulate": "(clisk.live/turbulate 0.2 clisk.live/snoise)",
        "gradient": "(clisk.live/gradient (clisk.live/x clisk.live/pos))",
        
        # Operators & Math helpers
        "v+": "(clisk.live/v+ clisk.live/pos [1.0 2.0 3.0 4.0])",
        "v*": "(clisk.live/v* clisk.live/pos [2.0 2.0 2.0 2.0])",
        "v-": "(clisk.live/v- clisk.live/pos [0.5 0.5 0.5 0.5])",
        "vdivide": "(clisk.live/vdivide clisk.live/pos [2.0 2.0 2.0 2.0])",
        "vpow": "(clisk.live/vpow clisk.live/pos [2.0 2.0 2.0 2.0])",
        "vmod": "(clisk.live/vmod clisk.live/pos [1.0 1.0 1.0 1.0])",
        "vmin": "(clisk.live/vmin clisk.live/pos [0.5 0.5 0.5 0.5])",
        "vmax": "(clisk.live/vmax clisk.live/pos [0.5 0.5 0.5 0.5])",
        "dot": "(clisk.live/dot clisk.live/pos clisk.live/pos)",
        "cross3": "(clisk.live/cross3 clisk.live/pos [0.0 1.0 0.0 0.0])",
        "vconcat": "(clisk.live/vconcat clisk.live/pos [1.0])",
        "average": "(clisk.live/average clisk.live/pos [1.0 2.0 3.0 4.0])",
        "adjust-hue": "(clisk.live/adjust-hue 0.25 clisk.live/pos)",
        "adjust-hsl": "(clisk.live/adjust-hsl [0.1 0.2 0.3] clisk.live/pos)",
        "checker": "(clisk.live/checker [0.0 0.0 0.0 1.0] [1.0 1.0 1.0 1.0])",
        
        # Ternary functions
        "lerp": "(clisk.live/lerp 0.0 1.0 clisk.live/pos)",
        "clamp": "(clisk.live/clamp clisk.live/pos 0.0 1.0)",
        "vif": "(clisk.live/vif clisk.live/pos [1.0 0.0 0.0 1.0] [0.0 0.0 1.0 1.0])"
    }
    
    # Process all functions
    all_fns = [
        (term_fns, "term"),
        (unary_fns, "unary"),
        (binary_fns, "binary"),
        (ternary_fns, "ternary")
    ]
    
    generated_count = 0
    for fn_list, cat in all_fns:
        for fn in fn_list:
            # Determine Clojure code content
            if fn in custom_templates:
                content = custom_templates[fn]
            elif cat == "term":
                content = f"clisk.live/{fn}"
            elif cat == "unary":
                content = f"(clisk.live/{fn} clisk.live/pos)"
            elif cat == "binary":
                # Fallback for general binary function
                content = f"(clisk.live/{fn} clisk.live/pos 1.0)"
            else:
                # Fallback for general ternary function
                content = f"(clisk.live/{fn} clisk.live/pos 1.0 2.0)"
            
            # Format filename to be safe (replacing operators)
            safe_name = fn.replace('+', 'add').replace('*', 'mul').replace('-', '_')
            filename = f"test_{safe_name}.clj"
            filepath = os.path.join(cases_dir, filename)
            
            with open(filepath, "w") as out:
                out.write(content + "\n")
            
            generated_count += 1
            
    print(f"Successfully generated {generated_count} test cases in {cases_dir}")

if __name__ == "__main__":
    main()
