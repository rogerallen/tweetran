__device__ vfloat pixel_fn1(vfloat pos)
{
    vfloat atom5 = vfloat( 3.0042 );
    vfloat var4 = adjust_hsl(atom5, pos);
    vfloat var3 = red_from_hsl(var4);
    return var3;
}
__device__ vfloat pixel_fn0(vfloat pos)
{
    vfloat atom2 = vfloat( 0.5 );
    vfloat var0 = scale(pos, atom2, pixel_fn1);
    return var0;
}
