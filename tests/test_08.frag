// --------------------------------------------------------------------------------
vfloat pixel_fn1(vfloat pos)
{
    vfloat atom5 = make_vfloat( 3.00420 );
    vfloat var4 = adjust_hsl(atom5, pos);
    vfloat var3 = red_from_hsl(var4);
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
    vfloat atom2 = make_vfloat( 0.50000 );
    vfloat var0 = scale_pixel_fn1(pos, atom2);
    return var0;
}
