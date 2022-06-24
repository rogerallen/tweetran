//
// C++ prototype file for generating tweegeemee images leveraging the
// same code as the CUDA source.  Compile with the output from gen_cuda
// like so:
//
// g++ -DGEN_CUDA_OUTPUT_FILE="../tests/test_12.cuh" -I../cuda proto.cpp -o c_retwee_test_12
//
#include <iostream>
#include <time.h>

#pragma GCC diagnostic push
#pragma GCC diagnostic ignored "-Wmissing-field-initializers"
#pragma GCC diagnostic ignored "-Wimplicit-fallthrough="
#define STB_IMAGE_WRITE_IMPLEMENTATION
#include "stb_image_write.h"
#pragma GCC diagnostic pop

struct float3 {
    float x, y, z;
};
static float3 make_float3(float x, float y, float z)
{
    float3 result = {x, y, z};
    return result;
}
struct float4 {
    float x, y, z, w;
};
static float4 make_float4(float x, float y, float z, float w)
{
    float4 result = {x, y, z, w};
    return result;
}
#define __global__ /*__global__*/
#define __device__ /*__device__*/
#define NO_CUDA_RENDER
#define __double_as_longlong(x) (*((long long *)(&x)))

#include "clisk.cuh"
// gen_cuda output file to be included here
#include GEN_CUDA_OUTPUT_FILE

void render(uint8_t *fb, int image_width, int image_height)
{
    for (int y = 0; y < image_height; ++y) {
        for (int x = 0; x < image_width; ++x) {
            float u = 1.0 * x / image_width;
            float v = 1.0 * y / image_height;
            float3 pixel = render_pixel(make_float4(u, v, 0.0, 0.0));
            fb[y * image_width * 3 + x * 3 + 0] = uint8_t(255.99 * clamp01(pixel.x));
            fb[y * image_width * 3 + x * 3 + 1] = uint8_t(255.99 * clamp01(pixel.y));
            fb[y * image_width * 3 + x * 3 + 2] = uint8_t(255.99 * clamp01(pixel.z));
        }
    }
}

int main(/*int argc, char **argv*/)
{

    int image_width = 720;
    int image_height = 720;
    int tx = 8;
    int ty = 8;

    std::cerr << "Rendering a " << image_width << "x" << image_height << " image ";
    std::cerr << "in " << tx << "x" << ty << " blocks.\n";

    int num_pixels = image_width * image_height;

    // allocate FB
    uint8_t *fb = new uint8_t[3 * num_pixels];

    clock_t start, stop;
    start = clock();
    render(fb, image_width, image_height);
    stop = clock();
    double timer_seconds = ((double)(stop - start)) / CLOCKS_PER_SEC;
    std::cerr << "took " << timer_seconds << " seconds.\n";

    // Output FB as PNG Image
    stbi_write_png("proto.png", image_width, image_height, 3, (const void *)fb,
                   image_width * 3 * sizeof(uint8_t));

    delete[] fb;
}
