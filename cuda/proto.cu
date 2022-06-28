#include <iostream>
#include <time.h>

#include "../src/utils.h"
#include "cudaErrorCheck.h"

#define JITIFY_PRINT_INSTANTIATION 0
#define JITIFY_PRINT_SOURCE 0
#define JITIFY_PRINT_LOG 0
#define JITIFY_PRINT_PTX 0
//#define JITIFY_PRINT_LINKER_LOG 0
#define JITIFY_PRINT_LAUNCH 0
#include "jitify.hpp"

#pragma GCC diagnostic push
#pragma GCC diagnostic ignored "-Wmissing-field-initializers"
#pragma GCC diagnostic ignored "-Wimplicit-fallthrough="
#define STB_IMAGE_WRITE_IMPLEMENTATION
#include "stb_image_write.h"
#pragma GCC diagnostic pop

int main(int argc, char **argv)
{
    if (argc != 3) {
        std::cerr << "USAGE: proto infile.cuh outfile.png\n";
        std::exit(1);
    }
    std::string source_path = argv[1];
    std::string dest_png{argv[2]};

    int magnification = 4;
    int image_width = 720 * magnification;
    int image_height = 720 * magnification;
    int surface_width = image_width;
    int surface_height = image_height;
    assert(surface_width >= image_width);
    assert(surface_height >= image_height);
    int tx = 16;
    int ty = 16;

    std::cerr << "Rendering a " << image_width << "x" << image_height << " image ";
    // std::cerr << "to a " << surface_width << "x" << surface_height << " surface ";
    std::cerr << "in " << tx << "x" << ty << " blocks using the GPU.\n";

    // pan around the image by moving the upper-left corner
    float U0 = 0.0, V0 = 0.0, W0 = 0.0, T0 = 0.0;
    // zoom into the image by adjusting these (> 1 zooms out, < 1 zooms in)
    float dU = 1.0, dV = 1.0;

    float4 image_origin = make_float4(U0, V0, W0, T0);
    float2 image_delta = make_float2(dU, dV);
    std::cerr << "Origin: " << U0 << ", " << V0 << ", " << W0 << ", " << T0 << ".\n";
    std::cerr << " Delta: " << dU << ", " << dV << ".\n";

    int surface_pixels = surface_width * surface_height;
    size_t fb_bytes = 4 * surface_pixels * sizeof(uint8_t);

    // allocate Frame Buffer (FB) on the GPU
    uint8_t *fb;
    cudaErrChk(cudaMallocManaged((void **)&fb, fb_bytes));

    // nvrt compile code.  Requires a module name as first line.
    // Use JITIFY_OPTIONS="-I/path/to/this/tweegeemeetranspiler" if not running
    // from above the cuda directory.
    std::string proto_src = "proto\n"
                            "#include \"cuda/clisk.cuh\"\n" +
                            slurp(source_path);
    static jitify::JitCache kernel_cache;
    jitify::Program program = kernel_cache.program(proto_src);

    clock_t start, stop;
    start = clock();
    // Render to our FB
    dim3 blocks(image_width / tx + 1, image_height / ty + 1);
    dim3 threads(tx, ty);
    cuErrChk(program.kernel("render_rgba")
                 .instantiate()
                 .configure(blocks, threads)
                 .launch(fb, image_origin, image_delta, image_width, image_height, surface_width));
    cudaErrChk(cudaGetLastError());
    cudaErrChk(cudaDeviceSynchronize());
    stop = clock();
    double timer_seconds = ((double)(stop - start)) / CLOCKS_PER_SEC;
    std::cerr << "took " << timer_seconds << " seconds.\n";

    // bring FB back to the CPU memory (no error check since this is just for performance and can fail on some systems)
    cudaMemPrefetchAsync(fb, fb_bytes, cudaCpuDeviceId);

    // Output FB as PNG Image
    std::cerr << "writing to " << dest_png << "...\n";
    stbi_write_png(dest_png.c_str(), image_width, image_height, 4, (const void *)fb,
                   surface_width * 4 * sizeof(uint8_t));

    cudaErrChk(cudaFree(fb));
}
