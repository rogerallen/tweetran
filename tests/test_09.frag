// --------------------------------------------------------------------------------
vfloat pixel_fn1(vfloat pos)
{
    vfloat var3 = vsnoise(pos);
    return var3;
}
vfloat gradient_pixel_fn1(vfloat pos)
{
    float epsilon = 0.0001;
    float oo_epsilon = 1.0 / epsilon;
    vfloat pos_dx = make_vfloat(pos.v.x + epsilon, pos.v.y, pos.v.z, pos.v.w);
    vfloat pos_dy = make_vfloat(pos.v.x, pos.v.y + epsilon, pos.v.z, pos.v.w);
    vfloat pos_dz = make_vfloat(pos.v.x, pos.v.y, pos.v.z + epsilon, pos.v.w);
    vfloat pos_dw = make_vfloat(pos.v.x, pos.v.y, pos.v.z, pos.v.w + epsilon);
    vfloat var1 = pixel_fn1(pos);
    vfloat var1_dx = pixel_fn1(pos_dx);
    vfloat var1_dy = pixel_fn1(pos_dy);
    vfloat var1_dz = pixel_fn1(pos_dz);
    vfloat var1_dw = pixel_fn1(pos_dw);
    float var0_dx = (var1_dx.v.x - var1.v.x) * oo_epsilon;
    float var0_dy = (var1_dy.v.y - var1.v.y) * oo_epsilon;
    float var0_dz = (var1_dz.v.z - var1.v.z) * oo_epsilon;
    float var0_dw = (var1_dw.v.w - var1.v.w) * oo_epsilon;
    vfloat var0 = make_vfloat(var0_dx, var0_dy, var0_dz, var0_dw);
    return var0;
}
vfloat pixel_fn0(vfloat pos)
{
    vfloat var1 = gradient_pixel_fn1(pos);
    vfloat var6 = vsnoise(pos);
    vfloat var7 = vnoise(pos);
    vfloat var5 = vmul(var6, var7);
    vfloat var0 = vadd(var1, var5);
    return var0;
}
