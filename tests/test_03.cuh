__device__ vfloat pixel_fn2(vfloat pos)
{
    vfloat var7 = vdot(pos, pos);
    vfloat var6 = blue_from_hsl(var7);
    return var6;
}
__device__ vfloat pixel_fn1(vfloat pos)
{
    vfloat atom5 = vfloat( 0.5 );
    vfloat var3 = scale(pos, atom5, pixel_fn2);
    return var3;
}
__device__ vfloat pixel_fn0(vfloat pos)
{
    vfloat atom2 = vfloat( -0.5, -0.5 );
    vfloat var0 = offset(pos, atom2, pixel_fn1);
    return var0;
}
