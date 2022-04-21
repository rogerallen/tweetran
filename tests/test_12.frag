// --------------------------------------------------------------------------------
vfloat pixel_fn2(vfloat pos)
{
    vfloat atom9 = make_vfloat( 1.00000, 0.50000, 0.00000, 0.00000 );
    vfloat atom10 = make_vfloat( 0.25000, 0.25000, 0.50000, 0.00000 );
    vfloat var7 = checker(pos, atom9, atom10);
    return var7;
}
vfloat pixel_fn1(vfloat pos)
{
    vfloat var5 = noise(pos);
    return var5;
}
vfloat scale_pixel_fn1(vfloat pos, vfloat scale)
{
    vec4 s = smear_vec4(scale);
    vec4 oos = 1.0 / s;
    vfloat pos1 = make_vfloat(pos.v * oos);
    vfloat var0 = pixel_fn1(pos1);
    return var0;
}
vfloat scale_pixel_fn2(vfloat pos, vfloat scale)
{
    vec4 s = smear_vec4(scale);
    vec4 oos = 1.0 / s;
    vfloat pos1 = make_vfloat(pos.v * oos);
    vfloat var0 = pixel_fn2(pos1);
    return var0;
}
vfloat pixel_fn0(vfloat pos)
{
    vfloat atom4 = make_vfloat( 1.00000, 1.00000, 1.00000, 10.00000 );
    vfloat var2 = scale_pixel_fn1(pos, atom4);
    vfloat var0 = scale_pixel_fn2(pos, var2);
    return var0;
}
