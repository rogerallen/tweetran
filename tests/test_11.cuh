__device__ vfloat pixel_fn1(vfloat pos)
{
    vfloat var3 = vnoise(pos);
    return var3;
}
__device__ vfloat pixel_fn0(vfloat pos)
{
    vfloat atom2 = vfloat( 1, 1, 1, 10 );
    vfloat var0 = scale(pos, atom2, vnoise);
    return var0;
}
