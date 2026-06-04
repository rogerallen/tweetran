#!/usr/bin/env python3
import os
import math
from PIL import Image

def calculate_rmse(image_path_a, image_path_b):
    if not os.path.exists(image_path_a) or not os.path.exists(image_path_b):
        raise FileNotFoundError(f"One of the images could not be found: {image_path_a} or {image_path_b}")

    img_a = Image.open(image_path_a).convert("RGB")
    img_b = Image.open(image_path_b).convert("RGB")
    
    if img_a.size != img_b.size:
        raise ValueError(f"Image sizes do not match: {img_a.size} vs {img_b.size}")
        
    pixels_a = list(img_a.getdata())
    pixels_b = list(img_b.getdata())
    
    total_squared_diff = 0.0
    num_pixels = len(pixels_a)
    
    for (r_a, g_a, b_a), (r_b, g_b, b_b) in zip(pixels_a, pixels_b):
        total_squared_diff += ((r_a - r_b) / 255.0) ** 2
        total_squared_diff += ((g_a - g_b) / 255.0) ** 2
        total_squared_diff += ((b_a - b_b) / 255.0) ** 2
        
    mean_squared_diff = total_squared_diff / (num_pixels * 3)
    return math.sqrt(mean_squared_diff)

def generate_diff_image(image_path_a, image_path_b, diff_output_path):
    img_a = Image.open(image_path_a).convert("RGB")
    img_b = Image.open(image_path_b).convert("RGB")
    
    width, height = img_a.size
    diff_img = Image.new("RGB", (width, height))
    
    pixels_a = img_a.getdata()
    pixels_b = img_b.getdata()
    diff_pixels = []
    
    for (r_a, g_a, b_a), (r_b, g_b, b_b) in zip(pixels_a, pixels_b):
        # Compute difference and scale by 5 to amplify subtle differences
        diff_r = min(255, abs(r_a - r_b) * 5)
        diff_g = min(255, abs(g_a - g_b) * 5)
        diff_b = min(255, abs(b_a - b_b) * 5)
        diff_pixels.append((diff_r, diff_g, diff_b))
        
    diff_img.putdata(diff_pixels)
    diff_img.save(diff_output_path)

if __name__ == "__main__":
    import sys
    if len(sys.argv) < 3:
        print("Usage: compare_images.py imageA.png imageB.png [diff_output.png]")
        sys.exit(1)
        
    img_a = sys.argv[1]
    img_b = sys.argv[2]
    
    try:
        rmse = calculate_rmse(img_a, img_b)
        print(f"RMSE: {rmse:.6f}")
        if len(sys.argv) == 4:
            generate_diff_image(img_a, img_b, sys.argv[3])
    except Exception as e:
        print(f"Error: {e}")
        sys.exit(1)
