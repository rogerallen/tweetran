// Part of WebGL translation of the Clisk Library https://github.com/mikera/clisk
// by Roger Allen for the purpose of making a transpiler.
// --------------------------------------------------------------------------------
#define M_PI 3.14159265358979323846

// --------------------------------------------------------------------------------
// vfloat code
struct vfloat {
  vec4 v;
  int components;
};
vfloat make_vfloat(vec4 x)
{
  vfloat r = vfloat(x, 4);
  return r;
}
vfloat make_vfloat(vec3 x)
{
  vfloat r = vfloat(vec4(x.xyz,0.0), 3);
  return r;
}
vfloat make_vfloat()
{
  vfloat r = vfloat( vec4(0.0,0.0,0.0,0.0), 0 );
  return r;
}
vfloat make_vfloat(float x)
{
  vfloat r = vfloat( vec4(x,0.0,0.0,0.0), 1 );
  return r;
}
vfloat make_vfloat(float x, float y)
{
  vfloat r = vfloat( vec4(x,y,0.0,0.0), 2);
  return r;
}
vfloat make_vfloat(float x, float y, float z)
{
  vfloat r = vfloat( vec4(x,y,z,0.0), 3);
  return r;
}
vfloat make_vfloat(float x, float y, float z, float w)
{
  vfloat r = vfloat( vec4(x,y,z,w), 4);
  return r;
}
vec4 get_vec4(vfloat x)
{
  return x.v;
}
vec4 smear_vec4(vfloat x)
{
  if(x.components == 1) {
    return x.v.xxxx;
  }
  return x.v;
}
vec3 get_vec3(vfloat x)
{
  return x.v.xyz;
}
vec3 smear_vec3(vfloat x)
{
  if(x.components == 1) {
    return x.v.xxx;
  }
  return x.v.xyz;
}
