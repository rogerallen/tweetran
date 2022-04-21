__device__ vfloat pixel_fn0(vfloat pos)
{
    vfloat atom7 = vfloat( -2.9192, 2.9694 );
    vfloat var5 = vmul(pos, atom7);
    vfloat var4 = min_component(var5);
    vfloat var3 = vround(var4);
    vfloat var2 = min_component(var3);
    vfloat atom10 = vfloat( 1.4514 );
    vfloat atom14 = vfloat( 1.6084, 0.1552 );
    vfloat var13 = lightness_from_rgb(atom14);
    vfloat var12 = vsqrt(var13);
    vfloat var11 = vabs(var12);
    vfloat var9 = adjust_hsl(atom10, var11);
    vfloat var8 = lightness_from_rgb(var9);
    vfloat var1 = vadd(var2, var8);
    vfloat var0 = sigmoid(var1);
    return var0;
}
