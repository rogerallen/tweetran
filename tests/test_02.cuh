__device__ vfloat pixel_fn0(vfloat pos)
{
    vfloat atom2 = vfloat( 1, 0, 0, 0 );
    vfloat atom3 = vfloat( 0, 1, 0, 0 );
    vfloat var1 = vadd(atom2, atom3);
    vfloat atom5 = vfloat( 0, 0, 1, 0 );
    vfloat atom6 = vfloat( 0, 0, 0, 1 );
    vfloat var4 = vadd(atom5, atom6);
    vfloat var0 = vadd(var1, var4);
    return var0;
}
