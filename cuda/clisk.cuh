// My CUDA translation of the Clojure Clisk Library
// https://github.com/mikera/clisk
// Full list of functions used by Tweegeemee are here:
// https://github.com/rogerallen/tweegeemee/blob/master/src/tweegeemee/image.clj
//
// I'm using "JSFN" to mark functions to translate for JavaScript WebGL
// fragment shader code.  See ../js/cuh_fn_helper.py
//
// ======================================================================
#include <stdint.h>

// defines
#ifndef M_PI
#define M_PI 3.14159265358979323846
#endif

// ======================================================================
// main multi-component vector class
class vfloat {
    float4 v;
    int components = 0;

  public:
    __device__ int num_components() { return components; }
    __device__ vfloat(float4 x)
    {
        v = x;
        components = 4;
    }
    __device__ vfloat(float3 x)
    {
        v.x = x.x;
        v.y = x.y;
        v.z = x.z;
        v.w = 0.0;
        components = 3;
    }
    __device__ vfloat()
    {
        v = make_float4(0.0f, 0.0f, 0.0f, 0.0f);
        components = 0;
    }
    __device__ vfloat(float x)
    {
        v = make_float4(x, 0.0f, 0.0f, 0.0f);
        components = 1;
    }
    __device__ vfloat(float x, float y)
    {
        v = make_float4(x, y, 0.0f, 0.0f);
        components = 2;
    }
    __device__ vfloat(float x, float y, float z)
    {
        v = make_float4(x, y, z, 0.0f);
        components = 3;
    }
    __device__ vfloat(float x, float y, float z, float w)
    {
        v = make_float4(x, y, z, w);
        components = 4;
    }
    __device__ float4 get(bool smear = false)
    {
        if (smear && (components == 1)) {
            return make_float4(v.x, v.x, v.x, v.x);
        }
        else {
            return v;
        }
    }
    __device__ float3 get3(bool smear = false)
    {
        if (smear && (components == 1)) {
            return make_float3(v.x, v.x, v.x);
        }
        else {
            return make_float3(v.x, v.y, v.z);
        }
    }
    __device__ float x() { return v.x; }
    __device__ float y() { return (components == 1) ? v.x : v.y; }
    __device__ float z() { return (components == 1) ? v.x : v.z; }
    __device__ float w() { return (components == 1) ? v.x : v.w; }
};

// define some functions before use
__device__ vfloat vabs(vfloat arg0);
__device__ vfloat scale(vfloat pos, vfloat scale, vfloat (*fn)(vfloat));
__device__ vfloat offset(vfloat pos, vfloat scale, vfloat (*fn)(vfloat));
__device__ vfloat sigmoid(vfloat arg0);
__device__ vfloat vpow(vfloat arg0, vfloat arg1);
__device__ vfloat vif(vfloat arg0, vfloat arg1, vfloat arg2);
__device__ vfloat vfrac(vfloat arg0);
__device__ vfloat vadd(vfloat arg0, vfloat arg1);
__device__ vfloat vmul(vfloat arg0, vfloat arg1);
__device__ vfloat vlength(vfloat arg0);

// internal functions
#ifdef NO_CUDA_RENDER
// this exists in CUDA, but not in std C++
float rsqrtf(float a)
{
    return 1.0f / sqrtf(a);
}
#endif
__device__ float myfmodf(float a, float b)
{
    float r = fmodf(a, b);
    if (r < 0.0f) {
        r += b;
    }
    return r;
}
// JSFN logisticf
__device__ float logisticf(float x)
{
    return 1.0f / (1.0f + expf(-x));
}
// END JSFN
__device__ float4 addf4(float4 a, float4 b)
{
    float4 r;
    r.x = a.x + b.x;
    r.y = a.y + b.y;
    r.z = a.z + b.z;
    r.w = a.w + b.w;
    return r;
}

__device__ float3 addf3(float3 a, float3 b)
{
    float3 r;
    r.x = a.x + b.x;
    r.y = a.y + b.y;
    r.z = a.z + b.z;
    return r;
}

__device__ float clamp01(float v)
{
    return (v > 1.0) ? 1.0 : ((v < 0.0) ? 0.0 : v);
}

// ======================================================================
// main render functions
// pixel_fn0 is the pixel function that MUST be implemented
__device__ vfloat pixel_fn0(vfloat pos);

__device__ float3 render_pixel(float4 pos)
{
    vfloat var0 = pixel_fn0(pos);
    float4 out4 = var0.get(true);
    float3 out = make_float3(out4.x, out4.y, out4.z);
    return out;
}

#ifndef NO_CUDA_RENDER
// OpenGL will use BGRA buffer
__global__ void render_bgra(uint8_t *fb, float4 image_origin, float2 image_delta, int image_width, int image_height, int surface_width)
{
    const float TIME_SCALE = 10.0f; // FIXME parameter
    const int ROOT_N = 1;           // FIXME parameter
    const int N = ROOT_N * ROOT_N;  // N samples
    int i = threadIdx.x + blockIdx.x * blockDim.x;
    int j = threadIdx.y + blockIdx.y * blockDim.y;
    int pixel_index = j * surface_width * 4 + i * 4;
    if ((i >= image_width) || (j >= image_height))
        return;
    float u = image_origin.x + image_delta.x * (float(i) / image_width);
    float v = image_origin.y + image_delta.y * (float(j) / image_height);
    float du = image_delta.x / image_width / ROOT_N;
    float dv = image_delta.y / image_height / ROOT_N;
    // regular grid super-sampling (should add some rotation)
    float3 pixel = make_float3(0.0f, 0.0f, 0.0f);
    for (int dj = 0; dj < ROOT_N; dj++) {
        for (int di = 0; di < ROOT_N; di++) {
            float4 pos = make_float4(u + di * du, v + dj * dv, image_origin.z, image_origin.w / TIME_SCALE);
            float3 tmp = render_pixel(pos);
            pixel.x += tmp.x;
            pixel.y += tmp.y;
            pixel.z += tmp.z;
        }
    }
    fb[pixel_index + 2] = uint8_t(255.99 * clamp01(pixel.x / N));
    fb[pixel_index + 1] = uint8_t(255.99 * clamp01(pixel.y / N));
    fb[pixel_index + 0] = uint8_t(255.99 * clamp01(pixel.z / N));
    fb[pixel_index + 3] = uint8_t(255);
}

// stb PNG output will use RGBA buffer
__global__ void render_rgba(uint8_t *fb, float4 image_origin, float2 image_delta, int image_width, int image_height, int surface_width)
{
    int i = threadIdx.x + blockIdx.x * blockDim.x;
    int j = threadIdx.y + blockIdx.y * blockDim.y;
    int pixel_index = j * surface_width * 4 + i * 4;
    if ((i >= image_width) || (j >= image_height))
        return;
    float u = image_origin.x + image_delta.x * (float(i) / image_width);
    float v = image_origin.y + image_delta.y * (float(j) / image_height);
    float4 pos = make_float4(u, v, image_origin.z, image_origin.w);
    float3 pixel = render_pixel(pos);
    fb[pixel_index + 0] = uint8_t(255.99 * clamp01(pixel.x));
    fb[pixel_index + 1] = uint8_t(255.99 * clamp01(pixel.y));
    fb[pixel_index + 2] = uint8_t(255.99 * clamp01(pixel.z));
    fb[pixel_index + 3] = uint8_t(255);
}

#endif

// Noise
/*
 * Adapted from https://github.com/mikera/clisk/blob/develop/src/main/java/clisk/noise/Simplex.java
 * 4D case, only.
 */
__device__ static float4 grad4[] = {
    {0, 1, 1, 1},
    {0, 1, 1, -1},
    {0, 1, -1, 1},
    {0, 1, -1, -1},
    {0, -1, 1, 1},
    {0, -1, 1, -1},
    {0, -1, -1, 1},
    {0, -1, -1, -1},
    {1, 0, 1, 1},
    {1, 0, 1, -1},
    {1, 0, -1, 1},
    {1, 0, -1, -1},
    {-1, 0, 1, 1},
    {-1, 0, 1, -1},
    {-1, 0, -1, 1},
    {-1, 0, -1, -1},
    {1, 1, 0, 1},
    {1, 1, 0, -1},
    {1, -1, 0, 1},
    {1, -1, 0, -1},
    {-1, 1, 0, 1},
    {-1, 1, 0, -1},
    {-1, -1, 0, 1},
    {-1, -1, 0, -1},
    {1, 1, 1, 0},
    {1, 1, -1, 0},
    {1, -1, 1, 0},
    {1, -1, -1, 0},
    {-1, 1, 1, 0},
    {-1, 1, -1, 0},
    {-1, -1, 1, 0},
    {-1, -1, -1, 0}};

__device__ static int perm[] = {
    151, 160, 137, 91, 90, 15, 131, 13, 201, 95,
    96, 53, 194, 233, 7, 225, 140, 36, 103, 30, 69, 142, 8, 99, 37,
    240, 21, 10, 23, 190, 6, 148, 247, 120, 234, 75, 0, 26, 197, 62,
    94, 252, 219, 203, 117, 35, 11, 32, 57, 177, 33, 88, 237, 149, 56,
    87, 174, 20, 125, 136, 171, 168, 68, 175, 74, 165, 71, 134, 139,
    48, 27, 166, 77, 146, 158, 231, 83, 111, 229, 122, 60, 211, 133,
    230, 220, 105, 92, 41, 55, 46, 245, 40, 244, 102, 143, 54, 65, 25,
    63, 161, 1, 216, 80, 73, 209, 76, 132, 187, 208, 89, 18, 169, 200,
    196, 135, 130, 116, 188, 159, 86, 164, 100, 109, 198, 173, 186, 3,
    64, 52, 217, 226, 250, 124, 123, 5, 202, 38, 147, 118, 126, 255,
    82, 85, 212, 207, 206, 59, 227, 47, 16, 58, 17, 182, 189, 28, 42,
    223, 183, 170, 213, 119, 248, 152, 2, 44, 154, 163, 70, 221, 153,
    101, 155, 167, 43, 172, 9, 129, 22, 39, 253, 19, 98, 108, 110, 79,
    113, 224, 232, 178, 185, 112, 104, 218, 246, 97, 228, 251, 34, 242,
    193, 238, 210, 144, 12, 191, 179, 162, 241, 81, 51, 145, 235, 249,
    14, 239, 107, 49, 192, 214, 31, 181, 199, 106, 157, 184, 84, 204,
    176, 115, 121, 50, 45, 127, 4, 150, 254, 138, 236, 205, 93, 222,
    114, 67, 29, 24, 72, 243, 141, 128, 195, 78, 66, 215, 61, 156, 180,
    // repeat 256-entry table for ease of addressing.
    151, 160, 137, 91, 90, 15, 131, 13, 201, 95,
    96, 53, 194, 233, 7, 225, 140, 36, 103, 30, 69, 142, 8, 99, 37,
    240, 21, 10, 23, 190, 6, 148, 247, 120, 234, 75, 0, 26, 197, 62,
    94, 252, 219, 203, 117, 35, 11, 32, 57, 177, 33, 88, 237, 149, 56,
    87, 174, 20, 125, 136, 171, 168, 68, 175, 74, 165, 71, 134, 139,
    48, 27, 166, 77, 146, 158, 231, 83, 111, 229, 122, 60, 211, 133,
    230, 220, 105, 92, 41, 55, 46, 245, 40, 244, 102, 143, 54, 65, 25,
    63, 161, 1, 216, 80, 73, 209, 76, 132, 187, 208, 89, 18, 169, 200,
    196, 135, 130, 116, 188, 159, 86, 164, 100, 109, 198, 173, 186, 3,
    64, 52, 217, 226, 250, 124, 123, 5, 202, 38, 147, 118, 126, 255,
    82, 85, 212, 207, 206, 59, 227, 47, 16, 58, 17, 182, 189, 28, 42,
    223, 183, 170, 213, 119, 248, 152, 2, 44, 154, 163, 70, 221, 153,
    101, 155, 167, 43, 172, 9, 129, 22, 39, 253, 19, 98, 108, 110, 79,
    113, 224, 232, 178, 185, 112, 104, 218, 246, 97, 228, 251, 34, 242,
    193, 238, 210, 144, 12, 191, 179, 162, 241, 81, 51, 145, 235, 249,
    14, 239, 107, 49, 192, 214, 31, 181, 199, 106, 157, 184, 84, 204,
    176, 115, 121, 50, 45, 127, 4, 150, 254, 138, 236, 205, 93, 222,
    114, 67, 29, 24, 72, 243, 141, 128, 195, 78, 66, 215, 61, 156, 180};

// a Java file says this is fast.  Might want to check this, someday. FIXME
__device__ static int fastfloor(double x)
{
    int xi = (int)x;
    return x < xi ? xi - 1 : xi;
}

__device__ static double dot(float4 g, double x, double y, double z, double w)
{
    return g.x * x + g.y * y + g.z * z + g.w * w;
}

// 4D simplex noise
__device__ float simplex_snoise(vfloat pos) // FIXME (float4 pos)
{
    const double F4 = (sqrt(5.0) - 1.0) / 4.0;
    const double G4 = (5.0 - sqrt(5.0)) / 20.0;
    float x = pos.x();
    float y = pos.y();
    float z = pos.z();
    float w = pos.w();
    double n0, n1, n2, n3, n4; // Noise contributions from the five corners
    // Skew the (x,y,z,w) space to determine which cell of 24 simplices
    // we're in
    double s = (x + y + z + w) * F4; // Factor for 4D skewing
    int i = fastfloor(x + s);
    int j = fastfloor(y + s);
    int k = fastfloor(z + s);
    int l = fastfloor(w + s);
    double t = (i + j + k + l) * G4; // Factor for 4D unskewing
    double X0 = i - t;               // Unskew the cell origin back to (x,y,z,w) space
    double Y0 = j - t;
    double Z0 = k - t;
    double W0 = l - t;
    double x0 = x - X0; // The x,y,z,w distances from the cell origin
    double y0 = y - Y0;
    double z0 = z - Z0;
    double w0 = w - W0;
    // For the 4D case, the simplex is a 4D shape I won't even try to
    // describe.
    // To find out which of the 24 possible simplices we're in, we need to
    // determine the magnitude ordering of x0, y0, z0 and w0.
    // Six pair-wise comparisons are performed between each possible pair
    // of the four coordinates, and the results are used to rank the
    // numbers.
    int rankx = 0;
    int ranky = 0;
    int rankz = 0;
    int rankw = 0;
    if (x0 > y0)
        rankx++;
    else
        ranky++;
    if (x0 > z0)
        rankx++;
    else
        rankz++;
    if (x0 > w0)
        rankx++;
    else
        rankw++;
    if (y0 > z0)
        ranky++;
    else
        rankz++;
    if (y0 > w0)
        ranky++;
    else
        rankw++;
    if (z0 > w0)
        rankz++;
    else
        rankw++;
    int i1, j1, k1, l1; // The integer offsets for the second simplex corner
    int i2, j2, k2, l2; // The integer offsets for the third simplex corner
    int i3, j3, k3, l3; // The integer offsets for the fourth simplex corner
    // simplex[c] is a 4-vector with the numbers 0, 1, 2 and 3 in some order.
    // Many values of c will never occur, since e.g. x>y>z>w makes x<z, y<w and x<w
    // impossible. Only the 24 indices which have non-zero entries make any sense.
    // We use a thresholding to set the coordinates in turn from the largest magnitude.
    // Rank 3 denotes the largest coordinate.
    i1 = rankx >= 3 ? 1 : 0;
    j1 = ranky >= 3 ? 1 : 0;
    k1 = rankz >= 3 ? 1 : 0;
    l1 = rankw >= 3 ? 1 : 0;
    // Rank 2 denotes the second largest coordinate.
    i2 = rankx >= 2 ? 1 : 0;
    j2 = ranky >= 2 ? 1 : 0;
    k2 = rankz >= 2 ? 1 : 0;
    l2 = rankw >= 2 ? 1 : 0;
    // Rank 1 denotes the second smallest coordinate.
    i3 = rankx >= 1 ? 1 : 0;
    j3 = ranky >= 1 ? 1 : 0;
    k3 = rankz >= 1 ? 1 : 0;
    l3 = rankw >= 1 ? 1 : 0;
    // The fifth corner has all coordinate offsets = 1, so no need to compute that.
    double x1 = x0 - i1 + G4; // Offsets for second corner in (x,y,z,w) coords
    double y1 = y0 - j1 + G4;
    double z1 = z0 - k1 + G4;
    double w1 = w0 - l1 + G4;
    double x2 = x0 - i2 + 2.0 * G4; // Offsets for third corner in (x,y,z,w) coords
    double y2 = y0 - j2 + 2.0 * G4;
    double z2 = z0 - k2 + 2.0 * G4;
    double w2 = w0 - l2 + 2.0 * G4;
    double x3 = x0 - i3 + 3.0 * G4; // Offsets for fourth corner in (x,y,z,w) coords
    double y3 = y0 - j3 + 3.0 * G4;
    double z3 = z0 - k3 + 3.0 * G4;
    double w3 = w0 - l3 + 3.0 * G4;
    double x4 = x0 - 1.0 + 4.0 * G4; // Offsets for last corner in (x,y,z,w) coords
    double y4 = y0 - 1.0 + 4.0 * G4;
    double z4 = z0 - 1.0 + 4.0 * G4;
    double w4 = w0 - 1.0 + 4.0 * G4;
    // Work out the hashed gradient indices of the five simplex corners
    int ii = i & 255;
    int jj = j & 255;
    int kk = k & 255;
    int ll = l & 255;
    int gi0 = perm[ii + perm[jj + perm[kk + perm[ll]]]] % 32;
    int gi1 = perm[ii + i1 + perm[jj + j1 + perm[kk + k1 + perm[ll + l1]]]] % 32;
    int gi2 = perm[ii + i2 + perm[jj + j2 + perm[kk + k2 + perm[ll + l2]]]] % 32;
    int gi3 = perm[ii + i3 + perm[jj + j3 + perm[kk + k3 + perm[ll + l3]]]] % 32;
    int gi4 = perm[ii + 1 + perm[jj + 1 + perm[kk + 1 + perm[ll + 1]]]] % 32;
    // Calculate the contribution from the five corners
    double t0 = 0.6 - x0 * x0 - y0 * y0 - z0 * z0 - w0 * w0;
    if (t0 <= 0)
        n0 = 0.0;
    else {
        t0 *= t0;
        n0 = t0 * t0 * dot(grad4[gi0], x0, y0, z0, w0);
    }
    double t1 = 0.6 - x1 * x1 - y1 * y1 - z1 * z1 - w1 * w1;
    if (t1 <= 0)
        n1 = 0.0;
    else {
        t1 *= t1;
        n1 = t1 * t1 * dot(grad4[gi1], x1, y1, z1, w1);
    }
    double t2 = 0.6 - x2 * x2 - y2 * y2 - z2 * z2 - w2 * w2;
    if (t2 <= 0)
        n2 = 0.0;
    else {
        t2 *= t2;
        n2 = t2 * t2 * dot(grad4[gi2], x2, y2, z2, w2);
    }
    double t3 = 0.6 - x3 * x3 - y3 * y3 - z3 * z3 - w3 * w3;
    if (t3 <= 0)
        n3 = 0.0;
    else {
        t3 *= t3;
        n3 = t3 * t3 * dot(grad4[gi3], x3, y3, z3, w3);
    }
    double t4 = 0.6 - x4 * x4 - y4 * y4 - z4 * z4 - w4 * w4;
    if (t4 <= 0)
        n4 = 0.0;
    else {
        t4 *= t4;
        n4 = t4 * t4 * dot(grad4[gi4], x4, y4, z4, w4);
    }
    // Sum up and scale the result to cover the range [-1,1]
    return 27.0 * (n0 + n1 + n2 + n3 + n4);
}
// JSFN simplex_noise
__device__ float simplex_noise(vfloat pos) // FIXME (float4 pos)
{
    return 0.5 + 0.5 * simplex_snoise(pos);
}
// END JSFN
__device__ vfloat warp(vfloat pos, vfloat (*fn)(vfloat))
{
    return fn(pos);
}
// JSFN make_multi_fractal
__device__ vfloat make_multi_fractal(vfloat pos, vfloat (*fn)(vfloat))
{
    int octaves = 8;
    float lacunarity = 2.0;
    float gain = 0.5;
    float scale = 0.5;
    vfloat sum = vfloat(0.0, 0.0, 0.0, 0.0);
    for (int octave = 0; octave < octaves; octave++) {
        float pos_scale = powf(lacunarity, octave);
        vfloat pos1 = vfloat(pos.x() * pos_scale, pos.y() * pos_scale, pos.z() * pos_scale, pos.w() * pos_scale);
        vfloat val = warp(pos1, fn);
        float val_scale = scale * powf(gain, octave);
        val = vfloat(val.x() * val_scale, val.y() * val_scale, val.z() * val_scale, val.w() * val_scale);
        sum = vfloat(sum.x() + val.x(), sum.y() + val.y(), sum.z() + val.z(), sum.w() + val.w());
    }
    return sum;
}
// END JSFN
// Colors
// JSFN component_from_pqtf
__device__ float component_from_pqtf(float p, float q, float h)
{
    h = myfmodf(h, 1.0);
    if (h < 1.0 / 6.0)
        return p + (q - p) * 6.0 * h;
    if (h < 0.5)
        return q;
    if (h < 2.0 / 3.0)
        return p + (q - p) * (2.0 / 3.0 - h) * 6.0;
    return p;
}
// JSFN red_from_hslf
__device__ float red_from_hslf(float h, float s, float l)
{
    if (s == 0.0)
        return l;
    float q = (l < 0.5) ? (l * (1 + s)) : (l + s - l * s);
    float p = (2 * l) - q;
    return component_from_pqtf(p, q, h + 1.0 / 3.0);
}
// JSFN green_from_hslf
__device__ float green_from_hslf(float h, float s, float l)
{
    if (s == 0.0)
        return l;
    float q = (l < 0.5) ? (l * (1 + s)) : (l + s - l * s);
    float p = (2 * l) - q;
    return component_from_pqtf(p, q, h);
}
// JSFN blue_from_hslf
__device__ float blue_from_hslf(float h, float s, float l)
{
    if (s == 0.0)
        return l;
    float q = (l < 0.5) ? (l * (1 + s)) : (l + s - l * s);
    float p = (2 * l) - q;
    return component_from_pqtf(p, q, h - 1.0 / 3.0);
}
// JSFN huef
__device__ float huef(float r, float g, float b)
{
    float M = fmaxf(r, fmaxf(g, b));
    float m = fminf(r, fminf(g, b));
    float C = M - m;
    if (C == 0.0f) {
        return 0.0f;
    }
    else if (M == r) {
        return myfmodf((g - b) / C, 6.0f) / 6.0f;
    }
    else if (M == g) {
        return (((b - r) / C) + 2.0f) / 6.0f;
    }
    // M == b
    return (((r - g) / C) + 4.0f) / 6.0f;
}
// JSFN saturationf
__device__ float saturationf(float r, float g, float b)
{
    float M = fmaxf(r, fmaxf(g, b));
    float m = fminf(r, fminf(g, b));
    float C = M - m;
    float L = (M + m) * 0.5f;
    if (C == 0.0f) {
        return 0.0f;
    }
    else {
        return C / (1.0 - fabsf(2.0f * L - 1.0f));
    }
}
// JSFN lightnessf
__device__ float lightnessf(float r, float g, float b)
{
    float M = fmaxf(r, fmaxf(g, b));
    float m = fminf(r, fminf(g, b));
    return (M + m) * 0.5f;
}
// JSFN rgb_from_hslf3
__device__ float3 rgb_from_hslf3(float3 a)
{
    float3 r;
    r.x = red_from_hslf(a.x, a.y, a.z);
    r.y = green_from_hslf(a.x, a.y, a.z);
    r.z = blue_from_hslf(a.x, a.y, a.z);
    return r;
}
// JSFN hsl_from_rgbf3
__device__ float3 hsl_from_rgbf3(float3 a)
{
    float3 r;
    r.x = huef(a.x, a.y, a.z);
    r.y = saturationf(a.x, a.y, a.z);
    r.z = lightnessf(a.x, a.y, a.z);
    return r;
}
// END JSFN
// ======================================================================
// public functions
// ======================================================================

// ======================================================================
// TERMINAL POS =========================================================
// ======================================================================
// JSFN vnoise IN pos OUT 1x4
__device__ vfloat vnoise(vfloat pos)
{
    return vfloat(
        simplex_noise(make_float4(pos.x() + -120.34, pos.y() + 340.21, pos.z() + -13.67, pos.w() + 56.78)),
        simplex_noise(make_float4(pos.x() + 12.301, pos.y() + 70.261, pos.z() + -167.678, pos.w() + 34.568)),
        simplex_noise(make_float4(pos.x() + 78.676, pos.y() + -178.678, pos.z() + -79.612, pos.w() + -80.111)),
        simplex_noise(make_float4(pos.x() + -78.678, pos.y() + 7.6789, pos.z() + 200.567, pos.w() + 124.099)));
}
// JSFN vsnoise IN pos OUT 1x4
__device__ vfloat vsnoise(vfloat pos)
{
    return vfloat(
        simplex_snoise(make_float4(pos.x() + -120.34, pos.y() + 340.21, pos.z() + -13.67, pos.w() + 56.78)),
        simplex_snoise(make_float4(pos.x() + 12.301, pos.y() + 70.261, pos.z() + -167.678, pos.w() + 34.568)),
        simplex_snoise(make_float4(pos.x() + 78.676, pos.y() + -178.678, pos.z() + -79.612, pos.w() + -80.111)),
        simplex_snoise(make_float4(pos.x() + -78.678, pos.y() + 7.6789, pos.z() + 200.567, pos.w() + 124.099)));
}
// JSFN noise IN pos OUT 1x1
__device__ vfloat noise(vfloat pos)
{
    return vfloat(simplex_noise(make_float4(pos.x(), pos.y(), pos.z(), pos.w())));
}
// JSFN snoise IN pos OUT 1x1
__device__ vfloat snoise(vfloat pos)
{
    return vfloat(simplex_snoise(make_float4(pos.x(), pos.y(), pos.z(), pos.w())));
}
// JSFN plasma IN pos OUT 1x1
__device__ vfloat plasma(vfloat pos)
{
    return make_multi_fractal(pos, noise);
}
// JSFN splasma IN pos OUT 1x1
__device__ vfloat splasma(vfloat pos)
{
    return make_multi_fractal(pos, snoise);
}
// JSFN vabs_snoise
__device__ vfloat vabs_snoise(vfloat pos)
{
    return vabs(snoise(pos));
}
// JSFN vabs_vsnoise
__device__ vfloat vabs_vsnoise(vfloat pos)
{
    return vabs(vsnoise(pos));
}
// JSFN turbulence
__device__ vfloat turbulence(vfloat pos)
{
    return make_multi_fractal(pos, vabs_snoise);
}
// JSFN vturbulence
__device__ vfloat vturbulence(vfloat pos)
{
    return make_multi_fractal(pos, vabs_vsnoise);
}
// JSFN vplasma
__device__ vfloat vplasma(vfloat pos)
{
    return vfloat(
        plasma(make_float4(pos.x() + -120.34, pos.y() + 340.21, pos.z() + -13.67, pos.w() + 56.78)).x(),
        plasma(make_float4(pos.x() + 12.301, pos.y() + 70.261, pos.z() + -167.678, pos.w() + 34.568)).x(),
        plasma(make_float4(pos.x() + 78.676, pos.y() + -178.678, pos.z() + -79.612, pos.w() + -80.111)).x(),
        plasma(make_float4(pos.x() + -78.678, pos.y() + 7.6789, pos.z() + 200.567, pos.w() + 124.099)).x());
}
// JSFN vsplasma
__device__ vfloat vsplasma(vfloat pos)
{
    return vfloat(
        splasma(make_float4(pos.x() + -120.34, pos.y() + 340.21, pos.z() + -13.67, pos.w() + 56.78)).x(),
        splasma(make_float4(pos.x() + 12.301, pos.y() + 70.261, pos.z() + -167.678, pos.w() + 34.568)).x(),
        splasma(make_float4(pos.x() + 78.676, pos.y() + -178.678, pos.z() + -79.612, pos.w() + -80.111)).x(),
        splasma(make_float4(pos.x() + -78.678, pos.y() + 7.6789, pos.z() + 200.567, pos.w() + 124.099)).x());
}
// END
// A spotted monochome pattern
// JSFN spots_fn
__device__ vfloat spots_fn(vfloat pos)
{
    return 10 * (snoise(pos).x() - 0.3);
}
// JSFN spots
__device__ vfloat spots(vfloat pos)
{
    return sigmoid(scale(pos, 0.23, spots_fn));
}
// A blotchy monochome pattern
// JSFN blotches_fn
__device__ vfloat blotches_fn(vfloat pos)
{
    return 10 * (splasma(pos).x() - 0.2);
}
// JSFN blotches
__device__ vfloat blotches(vfloat pos)
{
    return sigmoid(scale(pos, 0.23, blotches_fn));
}
// JSFN clouds_fn
__device__ vfloat clouds_fn(vfloat pos)
{
    vfloat v = vpow(plasma(pos), 3);
    return make_float4(1.0 - v.x(), 1.0 - v.y(), 1.0 - v.z(), 1.0 - v.w());
}
// JSFN clouds
__device__ vfloat clouds(vfloat pos)
{
    return scale(pos, 0.3, clouds_fn);
}
// JSFN velvet_fn1
__device__ vfloat velvet_fn1(vfloat pos)
{
    return scale(pos, 0.2, noise);
}
// (warp (sigmoid (v* 2 vsnoise)) (scale 0.2 noise)))
// JSFN velvet
__device__ vfloat velvet(vfloat pos)
{
    vfloat n = vsnoise(pos);
    vfloat var0 = sigmoid(make_float4(2 * n.x(), 2 * n.y(), 2 * n.z(), 2 * n.w()));
    return warp(var0, velvet_fn1);
}
// END
// phash = (Util/dhash x y z t)
// scalar-hash-function = (phash ~'x ~'y ~'z ~'t)
// vector-hash = (vector-offsets scalar-hash-function)
// https://github.com/mikera/clisk/blob/develop/src/main/java/clisk/Util.java
long long longHash(long long sa)
{
    // java used unsigned right shift, so we convert a to unsigned
    unsigned long long a = (unsigned long long)sa;
    a ^= (a << 21);
    a ^= (a >> 35);
    a ^= (a << 4);
    return (long long)a;
}
long long rotateLeft(long long sx, int n)
{
    unsigned long long x = (unsigned long long)sx;
    return (x << n) | (x >> (64 - n));
}
long long hash(double x)
{
    return longHash(longHash(
        0x8000 + rotateLeft(longHash(__double_as_longlong(x)), 17)));
}
long long hash(double x, double y)
{
    return longHash(longHash(
        hash(x) + rotateLeft(longHash(__double_as_longlong(y)), 17)));
}
long long hash(double x, double y, double z)
{
    return longHash(longHash(
        hash(x, y) + rotateLeft(longHash(__double_as_longlong(z)), 17)));
}
long long hash(double x, double y, double z, double t)
{
    return longHash(longHash(
        hash(x, y, z) + rotateLeft(longHash(__double_as_longlong(t)), 17)));
}
double LONG_SCALE_FACTOR = 1.0 / (0x7fffffffffffffff + 1.0);
double dhash(double x, double y, double z, double t)
{
    long long h = hash(x, y, z, t);
    return (h & 0x7fffffffffffffff) * LONG_SCALE_FACTOR;
}
__device__ vfloat grain(vfloat pos)
{
    return vfloat(
        dhash(pos.x() + -120.34, pos.y() + 340.21, pos.z() + -13.67, pos.w() + 56.78),
        dhash(pos.x() + 12.301, pos.y() + 70.261, pos.z() + -167.678, pos.w() + 34.568),
        dhash(pos.x() + 78.676, pos.y() + -178.678, pos.z() + -79.612, pos.w() + -80.111),
        dhash(pos.x() + -78.678, pos.y() + 7.6789, pos.z() + 200.567, pos.w() + 124.099));
}
// (def agate
//  "A monochrome agate-style rock texture"
//  (scale 0.3
//    (offset
//      (v* 4 plasma)
//      (colour-map [[0 0] [0.05 0.5] [0.5 1.0] [0.95 0.5] [1.0 0]] vfrac))))
__device__ float agate_colour_map(float f)
{
    const float idxs[] = {0, 0.05, 0.5, 0.95, 1.0}; // must be monotonic increase
    const float vals[] = {0, 0.5, 1.0, 0.5, 0.0};
    int idx = 0;
    if (f <= idxs[0]) {
        return vals[0];
    }
    else if (f >= idxs[4]) {
        return vals[4];
    }
    else {
        while (idxs[idx] < f) {
            idx++;
        }
        // f is between idxs[idx-1] and idxs[idx]
        float df = (f - idxs[idx - 1]) / (idxs[idx] - idxs[idx - 1]);
        return (1.0 - df) * vals[idx - 1] + df * vals[idx];
    }
}
__device__ vfloat agate_fn2(vfloat pos)
{
    vfloat f = vfrac(pos);
    return vfloat(agate_colour_map(f.x()));
}
__device__ vfloat agate_fn1(vfloat pos)
{
    vfloat n = vmul(vfloat(4.0), plasma(pos));
    return offset(pos, n, agate_fn2);
}
__device__ vfloat agate(vfloat pos)
{
    return scale(pos, 0.3, agate_fn1);
}
// (def wood
//  "Spherical wood-like texture centred at origin"
//  (scale 0.1 (colour-map [[0 0] [1 1]] (vfrac length))))
__device__ vfloat wood_fn1(vfloat pos)
{
    // no need for "identity" colour-map
    return vfrac(vlength(pos));
}
__device__ vfloat wood(vfloat pos)
{
    return scale(pos, 0.1, wood_fn1);
}
// flecks   (scale 0.1 (v* 2.0 (apply-to-components `min vnoise))))
// JSFN flecks_fn1
__device__ vfloat flecks_fn1(vfloat pos)
{
    vfloat v0 = vnoise(pos);
    float v1 = fminf(2 * v0.x(), fminf(2 * v0.y(), fminf(2 * v0.z(), 2 * v0.w())));
    return vfloat(v1);
}
// JSFN flecks
__device__ vfloat flecks(vfloat pos)
{
    return scale(pos, vfloat(0.1), flecks_fn1);
}
// END
// ======================================================================
// MODIFY POS ===========================================================
// ======================================================================
// FN offset IN pos,1x4,fn OUT 1x4
__device__ vfloat offset(vfloat pos, vfloat offset, vfloat (*fn)(vfloat))
{
    float4 o = offset.get();
    vfloat pos1 = make_float4(pos.x() + o.x, pos.y() + o.y, pos.z() + o.z, pos.w() + o.w);
    vfloat var0 = warp(pos1, fn);
    return var0;
}
// FN scale IN pos,1x4,fn OUT 1x4
__device__ vfloat scale(vfloat pos, vfloat scale, vfloat (*fn)(vfloat))
{
    // scale *divides* by the scale factor.
    float4 s = scale.get(true);
    float4 oos = make_float4(1.0 / s.x, 1.0 / s.y, 1.0 / s.z, 1.0 / s.w);
    vfloat pos1 = make_float4(pos.x() * oos.x, pos.y() * oos.y, pos.z() * oos.z, pos.w() * oos.w);
    vfloat var0 = warp(pos1, fn);
    return var0;
}
// FN rotate IN pos,1x4,fn OUT 1x4
__device__ vfloat rotate(vfloat pos, vfloat angle, vfloat (*fn)(vfloat))
{
    float a = angle.x(); // angle is a scalar
    float x = pos.x();
    float y = pos.y();
    float z = pos.z();
    float t = pos.w();
    vfloat pos1 = make_float4(x * cosf(a) - y * sinf(a), y * cosf(a) + x * sin(a), z, t);
    vfloat var0 = warp(pos1, fn);
    return var0;
}
// FN gradient IN pos,fn OUT 1x4
__device__ vfloat gradient(vfloat pos, vfloat (*fn)(vfloat))
{
    float epsilon = 0.0001;
    float oo_epsilon = 1 / epsilon;
    vfloat pos_dx = make_float4(pos.x() + epsilon, pos.y(), pos.z(), pos.w());
    vfloat pos_dy = make_float4(pos.x(), pos.y() + epsilon, pos.z(), pos.w());
    vfloat pos_dz = make_float4(pos.x(), pos.y(), pos.z() + epsilon, pos.w());
    vfloat pos_dw = make_float4(pos.x(), pos.y(), pos.z(), pos.w() + epsilon);
    vfloat var1 = fn(pos);
    vfloat var1_dx = fn(pos_dx);
    vfloat var1_dy = fn(pos_dy);
    vfloat var1_dz = fn(pos_dz);
    vfloat var1_dw = fn(pos_dw);
    float var0_dx = (var1_dx.x() - var1.x()) * oo_epsilon;
    float var0_dy = (var1_dy.y() - var1.y()) * oo_epsilon;
    float var0_dz = (var1_dz.z() - var1.z()) * oo_epsilon;
    float var0_dw = (var1_dw.w() - var1.w()) * oo_epsilon;
    vfloat var0 = make_float4(var0_dx, var0_dy, var0_dz, var0_dw);
    return var0;
}
// ======================================================================
// UNARY ================================================================
// ======================================================================
// JSFN unity IN 1x4 OUT 1x4
__device__ vfloat unity(vfloat arg0)
{
    return arg0;
}
// JSFN triangle_wave IN 1x4 OUT 1x4
// Turns out this crashes if we call this, so we only ever get this function
// if lazy evaluation keeps us from actually calling it.  But, CUDA doesn't
// do lazy evaluation.  So, just return 0.
__device__ vfloat triangle_wave(vfloat arg0)
{
    return vfloat(0.0);
}
// JSFN x IN 1x4 OUT 1x1
__device__ vfloat x(vfloat arg0)
{
    float4 a = arg0.get(true);
    return vfloat(a.x);
}
// JSFN y IN 1x4 OUT 1x1
__device__ vfloat y(vfloat arg0)
{
    float4 a = arg0.get(true);
    return vfloat(a.y);
}
// JSFN z IN 1x4 OUT 1x1
__device__ vfloat z(vfloat arg0)
{
    float4 a = arg0.get(true);
    return vfloat(a.z);
}
// JSFN t IN 1x4 OUT 1x1
__device__ vfloat t(vfloat arg0)
{
    float4 a = arg0.get(true);
    return vfloat(a.w);
}
// JSFN alpha IN 1x4 OUT 1x1
__device__ vfloat alpha(vfloat arg0)
{
    float4 a = arg0.get(true);
    return vfloat(a.w);
}
// JSFN min_component IN 1x4 OUT 1x1
__device__ vfloat min_component(vfloat arg0)
{
    float4 a = arg0.get(true);
    float r = fminf(a.x, fminf(a.y, fminf(a.z, a.w)));
    return vfloat(r);
}
// JSFN max_component IN 1x4 OUT 1x1
__device__ vfloat max_component(vfloat arg0)
{
    float4 a = arg0.get(true);
    float r = fmaxf(a.x, fmaxf(a.y, fmaxf(a.z, a.w)));
    return vfloat(r);
}
// JSFN vlength IN 1x4 OUT 1x1
__device__ vfloat vlength(vfloat arg0)
{
    float4 a = arg0.get(true);
    float r = sqrtf(a.x * a.x + a.y * a.y + a.z * a.z + a.w * a.w);
    return vfloat(r);
}
// JSFN vsin IN 1x4 OUT 1x4
__device__ vfloat vsin(vfloat arg0)
{
    float4 a = arg0.get(true);
    float4 r;
    r.x = sinf(a.x);
    r.y = sinf(a.y);
    r.z = sinf(a.z);
    r.w = sinf(a.w);
    return vfloat(r);
}
// JSFN vcos IN 1x4 OUT 1x4
__device__ vfloat vcos(vfloat arg0)
{
    float4 a = arg0.get(true);
    float4 r;
    r.x = cosf(a.x);
    r.y = cosf(a.y);
    r.z = cosf(a.z);
    r.w = cosf(a.w);
    return vfloat(r);
}
// JSFN vround IN 1x4 OUT 1x4
__device__ vfloat vround(vfloat arg0)
{
    float4 a = arg0.get(true);
    float4 r;
    r.x = roundf(a.x);
    r.y = roundf(a.y);
    r.z = roundf(a.z);
    r.w = roundf(a.w);
    return vfloat(r);
}
// JSFN vfloor IN 1x4 OUT 1x4
__device__ vfloat vfloor(vfloat arg0)
{
    float4 a = arg0.get(true);
    float4 r;
    r.x = floorf(a.x);
    r.y = floorf(a.y);
    r.z = floorf(a.z);
    r.w = floorf(a.w);
    return vfloat(r);
}
// END
__device__ float fracf(float x)
{
    return x - floorf(x);
}
// JSFN vfrac IN 1x4 OUT 1x4
__device__ vfloat vfrac(vfloat arg0)
{
    float4 a = arg0.get(true);
    float4 r;
    r.x = fracf(a.x);
    r.y = fracf(a.y);
    r.z = fracf(a.z);
    r.w = fracf(a.w);
    return vfloat(r);
}
// JSFN vsqrt IN 1x4 OUT 1x4
__device__ vfloat vsqrt(vfloat arg0)
{
    float4 a = arg0.get(true);
    float4 r;
    r.x = sqrtf(a.x);
    r.y = sqrtf(a.y);
    r.z = sqrtf(a.z);
    r.w = sqrtf(a.w);
    return vfloat(r);
}
// JSFN vabs IN 1x4 OUT 1x4
__device__ vfloat vabs(vfloat arg0)
{
    float4 a = arg0.get(true);
    float4 r;
    r.x = fabsf(a.x);
    r.y = fabsf(a.y);
    r.z = fabsf(a.z);
    r.w = fabsf(a.w);
    return vfloat(r);
}
// JSFN square IN 1x4 OUT 1x4
__device__ vfloat square(vfloat arg0)
{
    float4 a = arg0.get(true);
    float4 r;
    r.x = a.x * a.x;
    r.y = a.y * a.y;
    r.z = a.z * a.z;
    r.w = a.w * a.w;
    return vfloat(r);
}
// JSFN vnormalize IN 1x4 OUT 1x4
__device__ vfloat vnormalize(vfloat arg0)
{
    float4 a = arg0.get(true);
    float4 r;
    // use fast reciprocal sqrt & multiply for normalization
    float rlen = rsqrtf(a.x * a.x + a.y * a.y + a.z * a.z + a.w * a.w);
    r.x = a.x * rlen;
    r.y = a.y * rlen;
    r.z = a.z * rlen;
    r.w = a.w * rlen;
    return vfloat(r);
}
// JSFN sigmoid IN 1x4 OUT 1x4
__device__ vfloat sigmoid(vfloat arg0)
{
    float4 a = arg0.get(true);
    float4 r;
    r.x = logisticf(a.x);
    r.y = logisticf(a.y);
    r.z = logisticf(a.z);
    r.w = logisticf(a.w);
    return vfloat(r);
}
// JSFN theta IN 1x4 OUT 1x1
__device__ vfloat theta(vfloat arg0)
{
    float4 a = arg0.get(true);
    float r = M_PI + atan2f(a.y, a.x);
    return vfloat(r);
}
// JSFN radius IN 1x4 OUT 1x1
__device__ vfloat radius(vfloat arg0)
{
    float4 a = arg0.get(true);
    float r = sqrtf(a.x * a.x + a.y * a.y);
    return vfloat(r);
}
// JSFN polar IN 1x4 OUT 1x2
__device__ vfloat polar(vfloat arg0)
{
    float r = radius(arg0).x();
    float t = theta(arg0).x();
    return vfloat(r, t);
}
// JSFN height IN 1x4 OUT 1x1
__device__ vfloat height(vfloat arg0)
{
    float4 a = arg0.get(true);
    float r = a.z;
    return vfloat(r);
}
// JSFN height_normal IN 1x4 OUT 1x3
__device__ vfloat height_normal(vfloat arg0)
{
    vfloat v = gradient(arg0, z); // ??? I think this is right?
    float3 r;
    r.x = -v.x();
    r.y = -v.y();
    r.z = 1.0;
    return vfloat(r);
}
// JSFN hue_from_rgb IN 1x3(rgb) OUT 1x1
__device__ vfloat hue_from_rgb(vfloat arg0)
{
    float4 a = arg0.get(true);
    float r = huef(a.x, a.y, a.z);
    return vfloat(r);
}
// JSFN saturation_from_rgb IN 1x3(rgb) OUT 1x1
__device__ vfloat saturation_from_rgb(vfloat arg0)
{
    float4 a = arg0.get(true);
    float r = saturationf(a.x, a.y, a.z);
    return vfloat(r);
}
// JSFN lightness_from_rgb IN 1x3(rgb) OUT 1x1
__device__ vfloat lightness_from_rgb(vfloat arg0)
{
    float4 a = arg0.get(true);
    float r = lightnessf(a.x, a.y, a.z);
    return vfloat(r);
}
// JSFN red_from_hsl IN 1x3(rgb) OUT 1x1
__device__ vfloat red_from_hsl(vfloat arg0)
{
    float4 a = arg0.get(true); // FIXME get3
    float r = red_from_hslf(a.x, a.y, a.z);
    return vfloat(r);
}
// JSFN green_from_hsl IN 1x3(rgb) OUT 1x1
__device__ vfloat green_from_hsl(vfloat arg0)
{
    float4 a = arg0.get(true);
    float r = green_from_hslf(a.x, a.y, a.z);
    return vfloat(r);
}
// JSFN blue_from_hsl IN 1x3(rgb) OUT 1x1
__device__ vfloat blue_from_hsl(vfloat arg0)
{
    float4 a = arg0.get(true);
    float r = blue_from_hslf(a.x, a.y, a.z);
    return vfloat(r);
}
// JSFN rgb_from_hsl IN 1x3(rgb) OUT 1x3
__device__ vfloat rgb_from_hsl(vfloat arg0)
{
    float3 a = arg0.get3();
    float3 r = rgb_from_hslf3(a);
    return vfloat(r);
}
// JSFN hsl_from_rgb IN 1x3(rgb) OUT 1x3
__device__ vfloat hsl_from_rgb(vfloat arg0)
{
    float3 a = arg0.get3();
    float3 r = hsl_from_rgbf3(a);
    return vfloat(r);
}
// END
// ======================================================================
// BINARY ===============================================================
// ======================================================================
// JSFN vadd IN 2x4 OUT 1x4
__device__ vfloat vadd(vfloat arg0, vfloat arg1)
{
    float4 a = arg0.get(true);
    float4 b = arg1.get(true);
    float4 r;
    r.x = a.x + b.x;
    r.y = a.y + b.y;
    r.z = a.z + b.z;
    r.w = a.w + b.w;
    return vfloat(r);
}
// JSFN vsub IN 2x4 OUT 1x4
__device__ vfloat vsub(vfloat arg0, vfloat arg1)
{
    float4 a = arg0.get(true);
    float4 b = arg1.get(true);
    float4 r;
    r.x = a.x - b.x;
    r.y = a.y - b.y;
    r.z = a.z - b.z;
    r.w = a.w - b.w;
    return vfloat(r);
}
// JSFN vmul IN 2x4 OUT 1x4
__device__ vfloat vmul(vfloat arg0, vfloat arg1)
{
    float4 a = arg0.get(true);
    float4 b = arg1.get(true);
    float4 r;
    r.x = a.x * b.x;
    r.y = a.y * b.y;
    r.z = a.z * b.z;
    r.w = a.w * b.w;
    return vfloat(r);
}
// JSFN vdivide IN 2x4 OUT 1x4
__device__ vfloat vdivide(vfloat arg0, vfloat arg1)
{
    float4 a = arg0.get(true);
    float4 b = arg1.get(true);
    float4 r;
    r.x = a.x / b.x;
    r.y = a.y / b.y;
    r.z = a.z / b.z;
    r.w = a.w / b.w;
    return vfloat(r);
}
// JSFN vmin IN 2x4 OUT 1x4
__device__ vfloat vmin(vfloat arg0, vfloat arg1)
{
    float4 a = arg0.get(true);
    float4 b = arg1.get(true);
    float4 r;
    r.x = fminf(a.x, b.x);
    r.y = fminf(a.y, b.y);
    r.z = fminf(a.z, b.z);
    r.w = fminf(a.w, b.w);
    return vfloat(r);
}
// JSFN vmax IN 2x4 OUT 1x4
__device__ vfloat vmax(vfloat arg0, vfloat arg1)
{
    float4 a = arg0.get(true);
    float4 b = arg1.get(true);
    float4 r;
    r.x = fmaxf(a.x, b.x);
    r.y = fmaxf(a.y, b.y);
    r.z = fmaxf(a.z, b.z);
    r.w = fmaxf(a.w, b.w);
    return vfloat(r);
}
// JSFN vpow IN 2x4 OUT 1x4
__device__ vfloat vpow(vfloat arg0, vfloat arg1)
{
    float4 a = arg0.get(true);
    float4 b = arg1.get(true);
    float4 r;
    r.x = powf(a.x, b.x);
    r.y = powf(a.y, b.y);
    r.z = powf(a.z, b.z);
    r.w = powf(a.w, b.w);
    return vfloat(r);
}
// JSFN vmod IN 2x4 OUT 1x4
__device__ vfloat vmod(vfloat arg0, vfloat arg1)
{
    float4 a = arg0.get(true);
    float4 b = arg1.get(true);
    float4 r;
    r.x = myfmodf(a.x, b.x);
    r.y = myfmodf(a.y, b.y);
    r.z = myfmodf(a.z, b.z);
    r.w = myfmodf(a.w, b.w);
    return vfloat(r);
}
// JSFN vdot IN 2x4 OUT 1x1
__device__ vfloat vdot(vfloat arg0, vfloat arg1)
{
    float4 a = arg0.get();
    float4 b = arg1.get();
    float r = a.x * b.x + a.y * b.y + a.z * b.z + a.w * b.w;
    return vfloat(r);
}
// JSFN cross3 IN 2x3 OUT 1x3
__device__ vfloat cross3(vfloat arg0, vfloat arg1)
{
    float4 a = arg0.get(true);
    float4 b = arg1.get(true);
    float4 r;
    r.x = a.y * b.z - a.z * b.y;
    r.y = a.z * b.x - a.x * b.z;
    r.z = a.x * b.y - a.y * b.x;
    r.w = 0.0f;
    return vfloat(r);
}
// JSFN adjust_hsl IN 2x3(rgb) OUT 1x3
// (defn adjust-hsl [shift source] (rgb-from-hsl (v+ shift (hsl-from-rgb source))))
__device__ vfloat adjust_hsl(vfloat arg0, vfloat arg1)
{
    float3 a = arg0.get3(true);
    float3 b = arg1.get3();
    float3 v = rgb_from_hslf3(addf3(a, hsl_from_rgbf3(b)));
    return vfloat(v);
}
// JSFN adjust_hue IN 2x3(rgb) OUT 1x3
// (defn adjust-hue [shift source] (rgb-from-hsl (v+ [(component shift 0) 0 0] (hsl-from-rgb source))))
__device__ vfloat adjust_hue(vfloat arg0, vfloat arg1)
{
    float3 a = arg0.get3();
    float3 b = arg1.get3();
    float3 tmp = make_float3(a.x, 0.0f, 0.0f);
    float3 v = rgb_from_hslf3(addf3(tmp, hsl_from_rgbf3(b)));
    return vfloat(v);
}
// END
// FN turbulate(addpos) IN 3x4 OUT 1x4
// last argument must be function.  Hmm...definitely needs testing.
__device__ vfloat turbulate(vfloat pos, vfloat arg0, vfloat (*fn)(vfloat))
{
    vfloat v = vmul(arg0, turbulence(pos));
    return offset(pos, v, fn);
}
// JSFN checker(addpos) IN 3x4 OUT 1x4
__device__ vfloat checker(vfloat pos, vfloat arg0, vfloat arg1)
{
    float cond = (fracf(pos.x()) - 0.5) * (fracf(pos.y()) - 0.5);
    return vif(vfloat(cond), arg0, arg1);
}
// JSFN vconcat IN 2x? OUT 1x?
__device__ vfloat vconcat(vfloat arg0, vfloat arg1)
{
    int na = arg0.num_components();
    int nb = arg1.num_components();
    int out_comp = fminf(4, na + nb);
    float4 r;
    // convoluted, but hopefully works?
    r.x = (na >= 1) ? arg0.x() : arg1.x();
    if (na >= 2) {
        r.y = arg0.y();
    }
    else { // na = 0, 1
        r.y = (na == 1) ? arg1.x() : arg1.y();
    }
    if (na >= 3) {
        r.z = arg0.z();
    }
    else { // na = 0, 1, 2
        if (na == 0) {
            r.z = arg1.z();
        }
        else if (na == 1) {
            r.z = arg1.y();
        }
        else {
            r.z = arg1.x();
        }
    }
    if (na == 4) {
        r.w = arg0.w();
    }
    else { // na = 0, 1, 2, 3
        if (na == 0) {
            r.w = arg1.w();
        }
        else if (na == 1) {
            r.w = arg1.z();
        }
        else if (na == 2) {
            r.w = arg1.y();
        }
        else {
            r.w = arg1.x();
        }
    }
    switch (out_comp) {
    case 1:
        return vfloat(r.x);
    case 2:
        return vfloat(r.x, r.y);
    case 3:
        return vfloat(r.x, r.y, r.z);
    case 4:
        return vfloat(r.x, r.y, r.z, r.w);
    default:
        return vfloat();
    }
}
// JSFN average IN 2x4 OUT 1x4
__device__ vfloat average(vfloat arg0, vfloat arg1)
{
    float4 a = arg0.get(true);
    float4 b = arg1.get(true);
    float4 r;
    r.x = 0.5 * (a.x + b.x);
    r.y = 0.5 * (a.y + b.y);
    r.z = 0.5 * (a.z + b.z);
    r.w = 0.5 * (a.w + b.w);
    return vfloat(r);
}
// END
// ======================================================================
// TERNARY ==============================================================
// ======================================================================
// JSFN lerp IN 3x4 OUT 1x4
__device__ vfloat lerp(vfloat arg0, vfloat arg1, vfloat arg2)
{
    float4 a = arg0.get(true);
    float4 b = arg1.get(true);
    float4 c = arg2.get(true);
    float4 r;
    r.x = a.x * b.x + (1.0 - a.x) * c.x;
    r.y = a.y * b.y + (1.0 - a.y) * c.y;
    r.z = a.z * b.z + (1.0 - a.z) * c.z;
    r.w = a.w * b.w + (1.0 - a.w) * c.w;
    return vfloat(r);
}
// JSFN vclamp IN 3x4 OUT 1x4
__device__ vfloat vclamp(vfloat arg0, vfloat arg1, vfloat arg2)
{
    float4 a = arg0.get(true);
    float4 b = arg1.get(true);
    float4 c = arg2.get(true);
    float4 r;
    r.x = fmaxf(b.x, fminf(c.x, a.x));
    r.y = fmaxf(b.y, fminf(c.y, a.y));
    r.z = fmaxf(b.z, fminf(c.z, a.z));
    r.w = fmaxf(b.w, fminf(c.w, a.w));
    return vfloat(r);
}
// JSFN vif IN 3x4 OUT 1x4
__device__ vfloat vif(vfloat arg0, vfloat arg1, vfloat arg2)
{
    float condition = arg0.x();
    float4 a = arg1.get(true);
    float4 b = arg2.get(true);
    float4 r;
    r.x = (condition > 0.0) ? a.x : b.x;
    r.y = (condition > 0.0) ? a.y : b.y;
    r.z = (condition > 0.0) ? a.z : b.z;
    r.w = (condition > 0.0) ? a.w : b.w;
    return vfloat(r);
}
// JSFN average IN 3x4 OUT 1x4
__device__ vfloat average(vfloat arg0, vfloat arg1, vfloat arg2)
{
    float4 a = arg0.get(true);
    float4 b = arg1.get(true);
    float4 c = arg2.get(true);
    float4 r;
    r.x = 0.333333333333 * (a.x + b.x + c.x);
    r.y = 0.333333333333 * (a.y + b.y + c.y);
    r.z = 0.333333333333 * (a.z + b.z + c.z);
    r.w = 0.333333333333 * (a.w + b.w + c.w);
    return vfloat(r);
}
// JSFN vconcat IN 3x4 OUT 1x4
__device__ vfloat vconcat(vfloat arg0, vfloat arg1, vfloat arg2)
{
    return vconcat(vconcat(arg0, arg1), arg2);
}