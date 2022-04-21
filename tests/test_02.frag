// --------------------------------------------------------------------------------
vfloat pixel_fn0(vfloat pos)
{
    vfloat atom2 = make_vfloat( 1.00000, 0.00000, 0.00000, 0.00000 );
    vfloat atom3 = make_vfloat( 0.00000, 1.00000, 0.00000, 0.00000 );
    vfloat var1 = vadd(atom2, atom3);
    vfloat atom5 = make_vfloat( 0.00000, 0.00000, 1.00000, 0.00000 );
    vfloat atom6 = make_vfloat( 0.00000, 0.00000, 0.00000, 1.00000 );
    vfloat var4 = vadd(atom5, atom6);
    vfloat var0 = vadd(var1, var4);
    return var0;
}
