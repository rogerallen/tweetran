__device__ vfloat pixel_fn1(vfloat pos)
{
    vfloat var5 = snoise(pos);
    vfloat var4 = adjust_hsl(var5, pos);
    return var4;
}
__device__ vfloat pixel_fn0(vfloat pos)
{
    vfloat var2 = vsnoise(pos);
    vfloat var0 = scale(pos, var2, pixel_fn1);
    return var0;
}
