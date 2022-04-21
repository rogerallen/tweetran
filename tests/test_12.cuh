__device__ vfloat pixel_fn2(vfloat pos)
{
    vfloat atom9 = vfloat( 1, 0.5, 0, 0 );
    vfloat atom10 = vfloat( 0.25, 0.25, 0.5, 0 );
    vfloat var7 = checker(pos, atom9, atom10);
    return var7;
}
__device__ vfloat pixel_fn1(vfloat pos)
{
    vfloat var5 = noise(pos);
    return var5;
}
__device__ vfloat pixel_fn0(vfloat pos)
{
    vfloat atom4 = vfloat( 1, 1, 1, 10 );
    vfloat var2 = scale(pos, atom4, pixel_fn1);
    vfloat var0 = scale(pos, var2, pixel_fn2);
    return var0;
}
