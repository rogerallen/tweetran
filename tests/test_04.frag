// --------------------------------------------------------------------------------
vfloat pixel_fn0(vfloat pos)
{
    vfloat atom7 = make_vfloat( -2.91920, 2.96940 );
    vfloat var5 = vmul(pos, atom7);
    vfloat var4 = min_component(var5);
    vfloat var3 = vround(var4);
    vfloat var2 = min_component(var3);
    vfloat atom10 = make_vfloat( 1.45140 );
    vfloat atom14 = make_vfloat( 1.60840, 0.15520 );
    vfloat var13 = lightness_from_rgb(atom14);
    vfloat var12 = vsqrt(var13);
    vfloat var11 = vabs(var12);
    vfloat var9 = adjust_hsl(atom10, var11);
    vfloat var8 = lightness_from_rgb(var9);
    vfloat var1 = vadd(var2, var8);
    vfloat var0 = sigmoid(var1);
    return var0;
}
