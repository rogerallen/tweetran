// --------------------------------------------------------------------------------
vfloat pixel_fn1(vfloat pos)
{
    vfloat var5 = snoise(pos);
    vfloat var4 = adjust_hsl(var5, pos);
    return var4;
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
    vfloat var2 = vsnoise(pos);
    vfloat var0 = scale_pixel_fn1(pos, var2);
    return var0;
}
