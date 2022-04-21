// --------------------------------------------------------------------------------
vfloat pixel_fn2(vfloat pos)
{
    vfloat var7 = vdot(pos, pos);
    vfloat var6 = blue_from_hsl(var7);
    return var6;
}
vfloat scale_pixel_fn2(vfloat pos, vfloat scale)
{
    vec4 s = smear_vec4(scale);
    vec4 oos = 1.0 / s;
    vfloat pos1 = make_vfloat(pos.v * oos);
    vfloat var0 = pixel_fn2(pos1);
    return var0;
}
vfloat pixel_fn1(vfloat pos)
{
    vfloat atom5 = make_vfloat( 0.50000 );
    vfloat var3 = scale_pixel_fn2(pos, atom5);
    return var3;
}
vfloat offset_pixel_fn1(vfloat pos, vfloat offset)
{
    vec4 o = get_vec4(offset);
    vfloat pos1 = make_vfloat(pos.v + o);
    vfloat var0 = pixel_fn1(pos1);
    return var0;
}
vfloat pixel_fn0(vfloat pos)
{
    vfloat atom2 = make_vfloat( -0.50000, -0.50000 );
    vfloat var0 = offset_pixel_fn1(pos, atom2);
    return var0;
}
