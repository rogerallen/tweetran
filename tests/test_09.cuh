__device__ vfloat pixel_fn1(vfloat pos)
{
    vfloat var3 = vsnoise(pos);
    return var3;
}
__device__ vfloat pixel_fn0(vfloat pos)
{
    vfloat var1 = gradient(pos, pixel_fn1);
    vfloat var6 = vsnoise(pos);
    vfloat var7 = vnoise(pos);
    vfloat var5 = vmul(var6, var7);
    vfloat var0 = vadd(var1, var5);
    return var0;
}
