// --------------------------------------------------------------------------------
vfloat pixel_fn1(vfloat pos)
{
    vfloat var3 = vnoise(pos);
    return var3;
}
vfloat scale_pixel_fn1(vfloat pos, vfloat scale)
{
    vec4 s = smear_vec4(scale);
    vec4 oos = 1.0 / s;
    vfloat pos1 = make_vfloat(pos.v * oos);
    vfloat var0 = pixel_fn1(pos1);
    return var0;
}
vfloat pixel_fn0(vfloat pos)
{
    vfloat atom2 = make_vfloat( 1.00000, 1.00000, 1.00000, 10.00000 );
    vfloat var0 = scale_pixel_fn1(pos, atom2);
    return var0;
}
