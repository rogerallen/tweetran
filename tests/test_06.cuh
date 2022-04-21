__device__ vfloat pixel_fn0(vfloat pos)
{
    vfloat atom4 = vfloat( 3.14159 );
    vfloat var3 = adjust_hsl(atom4, pos);
    vfloat var2 = red_from_hsl(var3);
    vfloat var1 = vfloor(var2);
    vfloat var0 = red_from_hsl(var1);
    return var0;
}
