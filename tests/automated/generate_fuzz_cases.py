#!/usr/bin/env python3
import os
import sys
import random
import argparse
import glob

# Setup directories
base_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
cases_dir = os.path.join(base_dir, "tests", "cases")

# List of terminal functions/patterns (leaves)
term_fns = [
    "noise", "snoise", "plasma", "splasma", "vnoise", "vsnoise", "vplasma", "vsplasma",
    "grain", "turbulence", "vturbulence", "spots", "blotches", "agate", "clouds", "velvet", "flecks", "wood"
]

# Unary functions (non-modpos)
unary_fns = [
    "vsin", "vcos", "vabs", "vround", "vfloor", "vfrac", "square", "vsqrt", "sigmoid", "triangle-wave",
    "max-component", "min-component", "length", "normalize", "theta", "radius", "polar",
    "height", "hue-from-rgb", "lightness-from-rgb", "saturation-from-rgb", "hsl-from-rgb",
    "red-from-hsl", "green-from-hsl", "blue-from-hsl", "rgb-from-hsl", "x", "y", "z", "t", "alpha"
]

# Binary functions (non-modpos)
binary_fns = [
    "v+", "v*", "v-", "vdivide", "vpow", "vmod", "dot", "cross3", "vmin", "vmax",
    "checker", "adjust-hue", "adjust-hsl", "vconcat", "average"
]

# Ternary functions
ternary_fns = [
    "lerp", "clamp", "vif"
]

# Modpos functions (position-modifying coordinate transforms)
# IMPORTANT: In tweetran, the last parameter of a modpos function MUST be an active function/pattern,
# not a scalar or vector constant.
modpos_fns = ["scale", "offset", "rotate", "turbulate"]

def generate_vector(size=4):
    return "[" + " ".join(f"{random.uniform(-2.0, 2.0):.4f}" for _ in range(size)) + "]"

def generate_scalar():
    return f"{random.uniform(-2.0, 2.0):.4f}"

def generate_expr(depth, max_depth, must_be_fn=False, in_gradient=False):
    """
    Recursively generates a random Clisk expression tree.
    If must_be_fn is True, we avoid generating pure constants (reals/vectors),
    as required by position-modifying functions.
    """
    # Base case: reached max depth, return terminal
    if depth >= max_depth:
        if random.random() < 0.2:
            return "pos"
        else:
            return random.choice(term_fns)

    # Determine what categories are allowed
    categories = ["term", "unary", "binary", "ternary", "modpos"]
    if not must_be_fn:
        categories.append("constant")

    # Define weights for each category to ensure reasonable tree shapes
    if must_be_fn:
        weights = [0.20, 0.35, 0.30, 0.10, 0.05]
    else:
        weights = [0.15, 0.30, 0.30, 0.10, 0.10, 0.05]

    cat = random.choices(categories, weights=weights)[0]

    if cat == "constant":
        if random.random() < 0.5:
            return generate_scalar()
        else:
            # Clisk supports vectors of sizes 1 to 4
            return generate_vector(random.choice([1, 2, 3, 4]))

    elif cat == "term":
        if random.random() < 0.2:
            return "pos"
        else:
            return random.choice(term_fns)

    elif cat == "unary":
        allowed_unary = unary_fns
        if in_gradient:
            unstable = ["vsqrt", "vround", "vfloor", "vfrac", "vabs", "height", "height-normal"]
            allowed_unary = [f for f in unary_fns if f not in unstable]
        fn = random.choice(allowed_unary)
        arg = generate_expr(depth + 1, max_depth, in_gradient=in_gradient)
        return f"({fn} {arg})"

    elif cat == "binary":
        allowed_binary = binary_fns
        if in_gradient:
            unstable = ["vdivide", "vmod", "vmin", "vmax", "checker"]
            allowed_binary = [f for f in binary_fns if f not in unstable]
        fn = random.choice(allowed_binary)
        if fn in ["v+", "v*", "v-", "vdivide", "vpow", "vmod", "vmin", "vmax"]:
            arg1 = generate_expr(depth + 1, max_depth, in_gradient=in_gradient)
            # Avoid division by zero by using non-zero constants or safe expressions
            if fn in ["vdivide", "vmod"]:
                arg2 = f"{random.uniform(0.5, 3.0):.4f}" if random.random() < 0.5 else generate_vector(4)
            else:
                arg2 = generate_expr(depth + 1, max_depth, in_gradient=in_gradient)
            return f"({fn} {arg1} {arg2})"
        elif fn == "dot":
            arg1 = generate_expr(depth + 1, max_depth, in_gradient=in_gradient)
            arg2 = generate_expr(depth + 1, max_depth, in_gradient=in_gradient)
            return f"(dot {arg1} {arg2})"
        elif fn == "cross3":
            arg1 = generate_expr(depth + 1, max_depth, in_gradient=in_gradient)
            # cross3 expects a 3D/4D vector as its second parameter
            arg2 = generate_vector(4)
            return f"(cross3 {arg1} {arg2})"
        elif fn == "vconcat":
            arg1 = generate_expr(depth + 1, max_depth, in_gradient=in_gradient)
            arg2 = generate_expr(depth + 1, max_depth, in_gradient=in_gradient)
            return f"(vconcat {arg1} {arg2})"
        elif fn == "average":
            arg1 = generate_expr(depth + 1, max_depth, in_gradient=in_gradient)
            arg2 = generate_expr(depth + 1, max_depth, in_gradient=in_gradient)
            return f"(average {arg1} {arg2})"
        elif fn == "checker":
            arg1 = generate_expr(depth + 1, max_depth, in_gradient=in_gradient)
            arg2 = generate_expr(depth + 1, max_depth, in_gradient=in_gradient)
            return f"(checker {arg1} {arg2})"
        elif fn == "adjust-hue":
            angle = f"{random.uniform(0.0, 1.0):.4f}"
            arg = generate_expr(depth + 1, max_depth, in_gradient=in_gradient)
            return f"(adjust-hue {angle} {arg})"
        elif fn == "adjust-hsl":
            hsl = generate_vector(3)
            arg = generate_expr(depth + 1, max_depth, in_gradient=in_gradient)
            return f"(adjust-hsl {hsl} {arg})"

    elif cat == "ternary":
        allowed_ternary = ternary_fns
        if in_gradient:
            unstable = ["clamp", "vif"]
            allowed_ternary = [f for f in ternary_fns if f not in unstable]
        if not allowed_ternary:
            return "pos" if random.random() < 0.2 else random.choice(term_fns)
        fn = random.choice(allowed_ternary)
        if fn == "lerp":
            arg1 = generate_expr(depth + 1, max_depth, in_gradient=in_gradient)
            arg2 = generate_expr(depth + 1, max_depth, in_gradient=in_gradient)
            arg3 = generate_expr(depth + 1, max_depth, in_gradient=in_gradient)
            return f"(lerp {arg1} {arg2} {arg3})"
        elif fn == "clamp":
            arg = generate_expr(depth + 1, max_depth, in_gradient=in_gradient)
            min_val = f"{random.uniform(-1.0, 0.0):.4f}"
            max_val = f"{random.uniform(0.0, 2.0):.4f}"
            return f"(clamp {arg} {min_val} {max_val})"
        elif fn == "vif":
            arg1 = generate_expr(depth + 1, max_depth, in_gradient=in_gradient)
            arg2 = generate_expr(depth + 1, max_depth, in_gradient=in_gradient)
            arg3 = generate_expr(depth + 1, max_depth, in_gradient=in_gradient)
            return f"(vif {arg1} {arg2} {arg3})"

    elif cat == "modpos":
        allowed_modpos = modpos_fns
        if in_gradient:
            unstable = ["gradient"]
            allowed_modpos = [f for f in modpos_fns if f not in unstable]
        fn = random.choice(allowed_modpos)
        # Last argument MUST be a function or terminal function (e.g. snoise, pos, etc.)
        if fn == "scale":
            pattern = generate_expr(depth + 1, max_depth, must_be_fn=True, in_gradient=in_gradient)
            factor = f"{random.uniform(0.1, 5.0):.4f}"
            return f"(scale {factor} {pattern})"
        elif fn == "offset":
            pattern = generate_expr(depth + 1, max_depth, must_be_fn=True, in_gradient=in_gradient)
            vector = generate_vector(4)
            return f"(offset {vector} {pattern})"
        elif fn == "rotate":
            pattern = generate_expr(depth + 1, max_depth, must_be_fn=True, in_gradient=in_gradient)
            angle = f"{random.uniform(-3.14, 3.14):.4f}"
            return f"(rotate {angle} {pattern})"
        elif fn == "turbulate":
            pattern = generate_expr(depth + 1, max_depth, must_be_fn=True, in_gradient=in_gradient)
            factor = f"{random.uniform(0.05, 0.5):.4f}"
            return f"(turbulate {factor} {pattern})"
        elif fn == "gradient":
            pattern = generate_expr(depth + 1, max_depth, must_be_fn=True, in_gradient=True)
            return f"(gradient {pattern})"

    return "pos"

    return "pos"

def clean_fuzz_cases():
    files = glob.glob(os.path.join(cases_dir, "fuzz_*.clj"))
    for f in files:
        try:
            os.remove(f)
            print(f"Removed {os.path.basename(f)}")
        except Exception as e:
            print(f"Failed to remove {f}: {e}")
    print(f"Cleaned up {len(files)} fuzz cases.")

def main():
    parser = argparse.ArgumentParser(description="Generate random fuzzed Clisk test cases for tweegeemee.")
    parser.add_argument("--num-cases", type=int, default=50, help="Number of random test cases to generate")
    parser.add_argument("--max-depth", type=int, default=4, help="Maximum nesting depth of the AST")
    parser.add_argument("--seed", type=int, default=None, help="Random seed for reproducibility")
    parser.add_argument("--clean", action="store_true", help="Remove all fuzz_*.clj files from tests/cases/")
    
    args = parser.parse_args()
    
    if args.clean:
        clean_fuzz_cases()
        return

    if args.seed is not None:
        random.seed(args.seed)
        print(f"Using fixed random seed: {args.seed}")
    
    os.makedirs(cases_dir, exist_ok=True)
    
    generated = 0
    while generated < args.num_cases:
        expr = generate_expr(0, args.max_depth)
        # Avoid generating simple leaves/constants for fuzzing
        if not expr.startswith("("):
            continue
            
        # Wrap expression in rgb-from-hsl to guarantee a 3-component color vector output
        # (matching production tweegeemee output format and avoiding 1D scalar/vector render differences)
        expr = f"(rgb-from-hsl {expr})"
        
        filename = f"fuzz_{generated:03d}.clj"
        filepath = os.path.join(cases_dir, filename)
        
        with open(filepath, "w") as f:
            f.write(expr + "\n")
        generated += 1
        
    print(f"Successfully generated {generated} fuzzed cases in {cases_dir}")

if __name__ == "__main__":
    main()
