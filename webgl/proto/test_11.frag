// Part of WebGL translation of the Clisk Library https://github.com/mikera/clisk
// by Roger Allen for the purpose of making a transpiler.
// --------------------------------------------------------------------------------
uniform vec3 iResolution;
uniform float iTime;
uniform vec2 uOffset;
uniform float uZoom;
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
// Part of WebGL translation of the Clisk Library https://github.com/mikera/clisk
// by Roger Allen for the purpose of making a transpiler.
// --------------------------------------------------------------------------------
// Noise
// simplex_snoise via https://gist.github.com/patriciogonzalezvivo/670c22f3966e662d2f83

//	Simplex 4D Noise 
//	by Ian McEwan, Ashima Arts
//
vec4 permute(vec4 x){return mod(((x*34.0)+1.0)*x, 289.0);}
float permute(float x){return floor(mod(((x*34.0)+1.0)*x, 289.0));}
vec4 taylorInvSqrt(vec4 r){return 1.79284291400159 - 0.85373472095314 * r;}
float taylorInvSqrt(float r){return 1.79284291400159 - 0.85373472095314 * r;}

vec4 grad4(float j, vec4 ip){
  const vec4 ones = vec4(1.0, 1.0, 1.0, -1.0);
  vec4 p,s;

  p.xyz = floor( fract (vec3(j) * ip.xyz) * 7.0) * ip.z - 1.0;
  p.w = 1.5 - dot(abs(p.xyz), ones.xyz);
  s = vec4(lessThan(p, vec4(0.0)));
  p.xyz = p.xyz + (s.xyz*2.0 - 1.0) * s.www; 

  return p;
}

float simplex_snoise(vec4 v){
  const vec2  C = vec2( 0.138196601125010504,  // (5 - sqrt(5))/20  G4
                        0.309016994374947451); // (sqrt(5) - 1)/4   F4
  // First corner
  vec4 i  = floor(v + dot(v, C.yyyy) );
  vec4 x0 = v -   i + dot(i, C.xxxx);

  // Other corners

  // Rank sorting originally contributed by Bill Licea-Kane, AMD (formerly ATI)
  vec4 i0;

  vec3 isX = step( x0.yzw, x0.xxx );
  vec3 isYZ = step( x0.zww, x0.yyz );
  //  i0.x = dot( isX, vec3( 1.0 ) );
  i0.x = isX.x + isX.y + isX.z;
  i0.yzw = 1.0 - isX;

  //  i0.y += dot( isYZ.xy, vec2( 1.0 ) );
  i0.y += isYZ.x + isYZ.y;
  i0.zw += 1.0 - isYZ.xy;

  i0.z += isYZ.z;
  i0.w += 1.0 - isYZ.z;

  // i0 now contains the unique values 0,1,2,3 in each channel
  vec4 i3 = clamp( i0, 0.0, 1.0 );
  vec4 i2 = clamp( i0-1.0, 0.0, 1.0 );
  vec4 i1 = clamp( i0-2.0, 0.0, 1.0 );

  //  x0 = x0 - 0.0 + 0.0 * C 
  vec4 x1 = x0 - i1 + 1.0 * C.xxxx;
  vec4 x2 = x0 - i2 + 2.0 * C.xxxx;
  vec4 x3 = x0 - i3 + 3.0 * C.xxxx;
  vec4 x4 = x0 - 1.0 + 4.0 * C.xxxx;

  // Permutations
  i = mod(i, 289.0); 
  float j0 = permute( permute( permute( permute(i.w) + i.z) + i.y) + i.x);
  vec4 j1 = permute( permute( permute( permute (
             i.w + vec4(i1.w, i2.w, i3.w, 1.0 ))
           + i.z + vec4(i1.z, i2.z, i3.z, 1.0 ))
           + i.y + vec4(i1.y, i2.y, i3.y, 1.0 ))
           + i.x + vec4(i1.x, i2.x, i3.x, 1.0 ));
  // Gradients
  // ( 7*7*6 points uniformly over a cube, mapped onto a 4-octahedron.)
  // 7*7*6 = 294, which is close to the ring size 17*17 = 289.

  vec4 ip = vec4(1.0/294.0, 1.0/49.0, 1.0/7.0, 0.0) ;

  vec4 p0 = grad4(j0,   ip);
  vec4 p1 = grad4(j1.x, ip);
  vec4 p2 = grad4(j1.y, ip);
  vec4 p3 = grad4(j1.z, ip);
  vec4 p4 = grad4(j1.w, ip);

  // Normalise gradients
  vec4 norm = taylorInvSqrt(vec4(dot(p0,p0), dot(p1,p1), dot(p2, p2), dot(p3,p3)));
  p0 *= norm.x;
  p1 *= norm.y;
  p2 *= norm.z;
  p3 *= norm.w;
  p4 *= taylorInvSqrt(dot(p4,p4));

  // Mix contributions from the five corners
  vec3 m0 = max(0.6 - vec3(dot(x0,x0), dot(x1,x1), dot(x2,x2)), 0.0);
  vec2 m1 = max(0.6 - vec2(dot(x3,x3), dot(x4,x4)            ), 0.0);
  m0 = m0 * m0;
  m1 = m1 * m1;
  return 49.0 * ( dot(m0*m0, vec3( dot( p0, x0 ), dot( p1, x1 ), dot( p2, x2 )))
               + dot(m1*m1, vec2( dot( p3, x3 ), dot( p4, x4 ) ) ) ) ;

}
// WebGL translation of the Clisk Library https://github.com/mikera/clisk
// by Roger Allen for the purpose of making a transpiler.
//
// Full list of functions used by Tweegeemee are here:
// https://github.com/rogerallen/tweegeemee/blob/master/src/tweegeemee/image.clj
// --------------------------------------------------------------------------------
// JSFN vabs IN 1x4 OUT 1x4
vfloat vabs(vfloat arg0) 
{
    vec4 a = smear_vec4(arg0);
    vec4 r = abs(a);
    return make_vfloat(r);
}
// JSFN vpow IN 2x4 OUT 1x4
vfloat vpow(vfloat arg0, vfloat arg1)
{
    vec4 a = smear_vec4(arg0);
    vec4 b = smear_vec4(arg1);
    vec4 r = pow(a,b);
    return make_vfloat(r);
}
// JSFN vif IN 3x4 OUT 1x4
vfloat vif(vfloat arg0, vfloat arg1, vfloat arg2)
{
    float condition = arg0.v.x;
    vec4 a = smear_vec4(arg1);
    vec4 b = smear_vec4(arg2);
    vec4 r;
    r.x = (condition > 0.0) ? a.x : b.x;
    r.y = (condition > 0.0) ? a.y : b.y;
    r.z = (condition > 0.0) ? a.z : b.z;
    r.w = (condition > 0.0) ? a.w : b.w;
    return make_vfloat(r);
}
// JSFN logisticf
float logisticf(float x)
{
    return 1.0 / (1.0 + exp(-x));
}
// JSFN sigmoid IN 1x4 OUT 1x4
vfloat sigmoid(vfloat arg0)
{
    vec4 a = smear_vec4(arg0);
    vec4 r;
    r.x = logisticf(a.x);
    r.y = logisticf(a.y);
    r.z = logisticf(a.z);
    r.w = logisticf(a.w);
    return make_vfloat(r);
}
// JSFN simplex_noise
float simplex_noise(vec4 pos)
{
    return 0.5 + 0.5 * simplex_snoise(pos);
}
// JSFN component_from_pqtf
float component_from_pqtf(float p, float q, float h)
{
    h = mod(h, 1.0);
    if (h < 1.0 / 6.0)
        return p + (q - p) * 6.0 * h;
    if (h < 0.5)
        return q;
    if (h < 2.0 / 3.0)
        return p + (q - p) * (2.0 / 3.0 - h) * 6.0;
    return p;
}
// JSFN red_from_hslf
float red_from_hslf(float h, float s, float l)
{
    if (s == 0.0)
        return l;
    float q = (l < 0.5) ? (l * (1.0 + s)) : (l + s - l * s);
    float p = (2.0 * l) - q;
    return component_from_pqtf(p, q, h + 1.0 / 3.0);
}
// JSFN green_from_hslf
float green_from_hslf(float h, float s, float l)
{
    if (s == 0.0)
        return l;
    float q = (l < 0.5) ? (l * (1.0 + s)) : (l + s - l * s);
    float p = (2.0 * l) - q;
    return component_from_pqtf(p, q, h);
}
// JSFN blue_from_hslf
float blue_from_hslf(float h, float s, float l)
{
    if (s == 0.0)
        return l;
    float q = (l < 0.5) ? (l * (1.0 + s)) : (l + s - l * s);
    float p = (2.0 * l) - q;
    return component_from_pqtf(p, q, h - 1.0 / 3.0);
}
// JSFN huef
float huef(float r, float g, float b)
{
    float M = max(r, max(g, b));
    float m = min(r, min(g, b));
    float C = M - m;
    if (C == 0.0) {
        return 0.0;
    }
    else if (M == r) {
        return mod((g - b) / C, 6.0) / 6.0;
    }
    else if (M == g) {
        return (((b - r) / C) + 2.0) / 6.0;
    }
    // M == b
    return (((r - g) / C) + 4.0) / 6.0;
}
// JSFN saturationf
float saturationf(float r, float g, float b)
{
    float M = max(r, max(g, b));
    float m = min(r, min(g, b));
    float C = M - m;
    float L = (M + m) * 0.5f;
    if (C == 0.0) {
        return 0.0;
    }
    else {
        return C / (1.0 - abs(2.0 * L - 1.0));
    }
}
// JSFN lightnessf
float lightnessf(float r, float g, float b)
{
    float M = max(r, max(g, b));
    float m = min(r, min(g, b));
    return (M + m) * 0.5f;
}
// JSFN rgb_from_hslf3
vec3 rgb_from_hslf3(vec3 a)
{
    vec3 r;
    r.x = red_from_hslf(a.x, a.y, a.z);
    r.y = green_from_hslf(a.x, a.y, a.z);
    r.z = blue_from_hslf(a.x, a.y, a.z);
    return r;
}
// JSFN hsl_from_rgbf3
vec3 hsl_from_rgbf3(vec3 a)
{
    vec3 r;
    r.x = huef(a.x, a.y, a.z);
    r.y = saturationf(a.x, a.y, a.z);
    r.z = lightnessf(a.x, a.y, a.z);
    return r;
}
// JSFN vnoise IN pos OUT 1x4
vfloat vnoise(vfloat pos)
{
    return make_vfloat(
        simplex_noise(vec4(pos.v.x + -120.34, pos.v.y + 340.21, pos.v.z + -13.67, pos.v.w + 56.78)),
        simplex_noise(vec4(pos.v.x + 12.301, pos.v.y + 70.261, pos.v.z + -167.678, pos.v.w + 34.568)),
        simplex_noise(vec4(pos.v.x + 78.676, pos.v.y + -178.678, pos.v.z + -79.612, pos.v.w + -80.111)),
        simplex_noise(vec4(pos.v.x + -78.678, pos.v.y + 7.6789, pos.v.z + 200.567, pos.v.w + 124.099)));
}
// JSFN vsnoise IN pos OUT 1x4
vfloat vsnoise(vfloat pos)
{
    return make_vfloat(
        simplex_snoise(vec4(pos.v.x + -120.34, pos.v.y + 340.21, pos.v.z + -13.67, pos.v.w + 56.78)),
        simplex_snoise(vec4(pos.v.x + 12.301, pos.v.y + 70.261, pos.v.z + -167.678, pos.v.w + 34.568)),
        simplex_snoise(vec4(pos.v.x + 78.676, pos.v.y + -178.678, pos.v.z + -79.612, pos.v.w + -80.111)),
        simplex_snoise(vec4(pos.v.x + -78.678, pos.v.y + 7.6789, pos.v.z + 200.567, pos.v.w + 124.099)));
}
// JSFN noise IN pos OUT 1x1
vfloat noise(vfloat pos)
{
    return make_vfloat(simplex_noise(vec4(pos.v.x, pos.v.y, pos.v.z, pos.v.w)));
}
// JSFN snoise IN pos OUT 1x1
vfloat snoise(vfloat pos)
{
    return make_vfloat(simplex_snoise(vec4(pos.v.x, pos.v.y, pos.v.z, pos.v.w)));
}
// JSFN vabs_snoise
vfloat vabs_snoise(vfloat pos)
{
    return vabs(snoise(pos));
}
// JSFN vabs_vsnoise
vfloat vabs_vsnoise(vfloat pos)
{
    return vabs(vsnoise(pos));
}
// JSGEN make_multi_fractal noise
vfloat make_multi_fractal_noise(vfloat pos)
{
    float octaves = 8.0;
    float lacunarity = 2.0;
    float gain = 0.5;
    float scale = 0.5;
    vfloat sum = make_vfloat(0.0, 0.0, 0.0, 0.0);
    for (float octave = 0.0; octave < octaves; octave += 1.0) {
        float pos_scale = pow(lacunarity, octave);
        vfloat pos1 = make_vfloat(pos.v * pos_scale);
        vfloat val = noise(pos1);
        float val_scale = scale * pow(gain, octave);
        val = make_vfloat(val.v * val_scale);
        sum = make_vfloat(sum.v + val.v);
    }
    return sum;
}
// JSGEN make_multi_fractal snoise
vfloat make_multi_fractal_snoise(vfloat pos)
{
    float octaves = 8.0;
    float lacunarity = 2.0;
    float gain = 0.5;
    float scale = 0.5;
    vfloat sum = make_vfloat(0.0, 0.0, 0.0, 0.0);
    for (float octave = 0.0; octave < octaves; octave += 1.0) {
        float pos_scale = pow(lacunarity, octave);
        vfloat pos1 = make_vfloat(pos.v * pos_scale);
        vfloat val = snoise(pos1);
        float val_scale = scale * pow(gain, octave);
        val = make_vfloat(val.v * val_scale);
        sum = make_vfloat(sum.v + val.v);
    }
    return sum;
}
// JSGEN make_multi_fractal vabs_snoise
vfloat make_multi_fractal_vabs_snoise(vfloat pos)
{
    float octaves = 8.0;
    float lacunarity = 2.0;
    float gain = 0.5;
    float scale = 0.5;
    vfloat sum = make_vfloat(0.0, 0.0, 0.0, 0.0);
    for (float octave = 0.0; octave < octaves; octave += 1.0) {
        float pos_scale = pow(lacunarity, octave);
        vfloat pos1 = make_vfloat(pos.v * pos_scale);
        vfloat val = vabs_snoise(pos1);
        float val_scale = scale * pow(gain, octave);
        val = make_vfloat(val.v * val_scale);
        sum = make_vfloat(sum.v + val.v);
    }
    return sum;
}
// JSGEN make_multi_fractal vabs_vsnoise
vfloat make_multi_fractal_vabs_vsnoise(vfloat pos)
{
    float octaves = 8.0;
    float lacunarity = 2.0;
    float gain = 0.5;
    float scale = 0.5;
    vfloat sum = make_vfloat(0.0, 0.0, 0.0, 0.0);
    for (float octave = 0.0; octave < octaves; octave += 1.0) {
        float pos_scale = pow(lacunarity, octave);
        vfloat pos1 = make_vfloat(pos.v * pos_scale);
        vfloat val = vabs_vsnoise(pos1);
        float val_scale = scale * pow(gain, octave);
        val = make_vfloat(val.v * val_scale);
        sum = make_vfloat(sum.v + val.v);
    }
    return sum;
}
// JSFN plasma IN pos OUT 1x1
vfloat plasma(vfloat pos)
{
    return make_multi_fractal_noise(pos);
}
// JSFN splasma IN pos OUT 1x1
vfloat splasma(vfloat pos)
{
    return make_multi_fractal_snoise(pos);
}
// JSFN turbulence
vfloat turbulence(vfloat pos)
{
    return make_multi_fractal_vabs_snoise(pos);
}
// JSFN vturbulence
vfloat vturbulence(vfloat pos)
{
    return make_multi_fractal_vabs_vsnoise(pos);
}
// JSFN vplasma
vfloat vplasma(vfloat pos)
{
    return make_vfloat(
        plasma(make_vfloat(pos.v.x + -120.34, pos.v.y + 340.21, pos.v.z + -13.67, pos.v.w + 56.78)).v.x,
        plasma(make_vfloat(pos.v.x + 12.301, pos.v.y + 70.261, pos.v.z + -167.678, pos.v.w + 34.568)).v.x,
        plasma(make_vfloat(pos.v.x + 78.676, pos.v.y + -178.678, pos.v.z + -79.612, pos.v.w + -80.111)).v.x,
        plasma(make_vfloat(pos.v.x + -78.678, pos.v.y + 7.6789, pos.v.z + 200.567, pos.v.w + 124.099)).v.x);
}
// JSFN vsplasma
vfloat vsplasma(vfloat pos)
{
    return make_vfloat(
        splasma(make_vfloat(pos.v.x + -120.34, pos.v.y + 340.21, pos.v.z + -13.67, pos.v.w + 56.78)).v.x,
        splasma(make_vfloat(pos.v.x + 12.301, pos.v.y + 70.261, pos.v.z + -167.678, pos.v.w + 34.568)).v.x,
        splasma(make_vfloat(pos.v.x + 78.676, pos.v.y + -178.678, pos.v.z + -79.612, pos.v.w + -80.111)).v.x,
        splasma(make_vfloat(pos.v.x + -78.678, pos.v.y + 7.6789, pos.v.z + 200.567, pos.v.w + 124.099)).v.x);
}
// JSFN spots_fn
vfloat spots_fn(vfloat pos)
{
    vfloat n = snoise(pos);
    return make_vfloat(10.0 * (n.v.x - 0.3));
}
// JSGEN scale spots_fn
vfloat scale_spots_fn(vfloat pos, vfloat scale)
{
    vec4 s = smear_vec4(scale);
    vec4 oos = 1.0 / s;
    vfloat pos1 = make_vfloat(pos.v * oos);
    vfloat var0 = spots_fn(pos1);
    return var0;
}
// JSFN spots
vfloat spots(vfloat pos)
{
    return sigmoid(scale_spots_fn(pos, make_vfloat(0.23)));
}
// A blotchy monochome pattern
// JSFN blotches_fn
vfloat blotches_fn(vfloat pos)
{
    vfloat n = splasma(pos);
    return make_vfloat(10.0 * (n.v.x - 0.2));
}
// JSGEN scale blotches_fn
vfloat scale_blotches_fn(vfloat pos, vfloat scale)
{
    vec4 s = smear_vec4(scale);
    vec4 oos = 1.0 / s;
    vfloat pos1 = make_vfloat(pos.v * oos);
    vfloat var0 = blotches_fn(pos1);
    return var0;
}
// JSFN blotches
vfloat blotches(vfloat pos)
{
    return sigmoid(scale_blotches_fn(pos, make_vfloat(0.23)));
}
// JSFN clouds_fn
vfloat clouds_fn(vfloat pos)
{
    vfloat v = vpow(plasma(pos), make_vfloat(3.0));
    return make_vfloat(1.0 - v.v.x, 1.0 - v.v.y, 1.0 - v.v.z, 1.0 - v.v.w);
}
// JSGEN scale clouds_fn
vfloat scale_clouds_fn(vfloat pos, vfloat scale)
{
    vec4 s = smear_vec4(scale);
    vec4 oos = 1.0 / s;
    vfloat pos1 = make_vfloat(pos.v * oos);
    vfloat var0 = clouds_fn(pos1);
    return var0;
}
// JSFN clouds
vfloat clouds(vfloat pos)
{
    return scale_clouds_fn(pos, make_vfloat(0.3));
}
// JSGEN scale noise
vfloat scale_noise(vfloat pos, vfloat scale)
{
    vec4 s = smear_vec4(scale);
    vec4 oos = 1.0 / s;
    vfloat pos1 = make_vfloat(pos.v * oos);
    vfloat var0 = noise(pos1);
    return var0;
}
// JSFN velvet_fn1
vfloat velvet_fn1(vfloat pos)
{
    return scale_noise(pos, make_vfloat(0.2));
}
// (warp (sigmoid (v* 2 vsnoise)) (scale 0.2 noise)))
// JSFN velvet
vfloat velvet(vfloat pos)
{
    vec4 n = get_vec4(vsnoise(pos));
    vfloat var0 = sigmoid(make_vfloat(n * 2.0));
    return velvet_fn1(var0);
}
// JSFN flecks_fn1
vfloat flecks_fn1(vfloat pos)
{
    vfloat v0 = vnoise(pos);
    float v1 = min(2.0 * v0.v.x, min(2.0 * v0.v.y, min(2.0 * v0.v.z, 2.0 * v0.v.w)));
    return make_vfloat(v1);
}
// JSGEN scale flecks_fn1
vfloat scale_flecks_fn1(vfloat pos, vfloat scale)
{
    vec4 s = smear_vec4(scale);
    vec4 oos = 1.0 / s;
    vfloat pos1 = make_vfloat(pos.v * oos);
    vfloat var0 = flecks_fn1(pos1);
    return var0;
}
// JSFN flecks
vfloat flecks(vfloat pos)
{
    return scale_flecks_fn1(pos, make_vfloat(0.1));
}
// JSFN x IN 1x4 OUT 1x1
vfloat x(vfloat arg0)
{
    vec4 a = smear_vec4(arg0);
    return make_vfloat(a.x);
}
// JSFN y IN 1x4 OUT 1x1
vfloat y(vfloat arg0)
{
    vec4 a = smear_vec4(arg0);
    return make_vfloat(a.y);
}
// JSFN z IN 1x4 OUT 1x1
vfloat z(vfloat arg0)
{
    vec4 a = smear_vec4(arg0);
    return make_vfloat(a.z);
}
// JSFN t IN 1x4 OUT 1x1
vfloat t(vfloat arg0)
{
    vec4 a = smear_vec4(arg0);
    return make_vfloat(a.w);
}
// JSFN alpha IN 1x4 OUT 1x1
vfloat alpha(vfloat arg0)
{
    vec4 a = smear_vec4(arg0);
    return make_vfloat(a.w);
}
// JSFN min_component IN 1x4 OUT 1x1
vfloat min_component(vfloat arg0)
{
    vec4 a = smear_vec4(arg0);
    float r = min(a.x, min(a.y, min(a.z, a.w)));
    return make_vfloat(r);
}
// JSFN max_component IN 1x4 OUT 1x1
vfloat max_component(vfloat arg0)
{
    vec4 a = smear_vec4(arg0);
    float r = max(a.x, max(a.y, max(a.z, a.w)));
    return make_vfloat(r);
}
// JSFN vlength IN 1x4 OUT 1x1
vfloat vlength(vfloat arg0)
{
    vec4 a = smear_vec4(arg0);
    float r = length(a);
    return make_vfloat(r);
}
// JSFN vsin IN 1x4 OUT 1x4
vfloat vsin(vfloat arg0)
{
    vec4 a = smear_vec4(arg0);
    vec4 r = sin(a);
    return make_vfloat(r);
}
// JSFN vcos IN 1x4 OUT 1x4
vfloat vcos(vfloat arg0)
{
    vec4 a = smear_vec4(arg0);
    vec4 r = cos(a);
    return make_vfloat(r);
}
// JSFN vround IN 1x4 OUT 1x4
vfloat vround(vfloat arg0)
{
    vec4 a = smear_vec4(arg0);
    vec4 r = round(a);
    return make_vfloat(r);
}
// JSFN vfloor IN 1x4 OUT 1x4
vfloat vfloor(vfloat arg0)
{
    vec4 a = smear_vec4(arg0);
    vec4 r = floor(a);
    return make_vfloat(r);
}
// JSFN vfrac IN 1x4 OUT 1x4
vfloat vfrac(vfloat arg0)
{
    vec4 a = smear_vec4(arg0);
    vec4 r = fract(a);
    return make_vfloat(r);
}
// JSFN vsqrt IN 1x4 OUT 1x4
vfloat vsqrt(vfloat arg0)
{
    vec4 a = smear_vec4(arg0);
    vec4 r = sqrt(a);
    return make_vfloat(r);
}
// JSFN square IN 1x4 OUT 1x4
vfloat square(vfloat arg0)
{
    vec4 a = smear_vec4(arg0);
    vec4 r = a * a;
    return make_vfloat(r);
}
// JSFN vnormalize IN 1x4 OUT 1x4 
vfloat vnormalize(vfloat arg0)
{
    vec4 a = smear_vec4(arg0);
    vec4 r = normalize(a);
    return make_vfloat(r);
}
// JSFN theta IN 1x4 OUT 1x1
vfloat theta(vfloat arg0)
{
    vec4 a = smear_vec4(arg0);
    float r = M_PI + atan(a.y, a.x);
    return make_vfloat(r);
}
// JSFN radius IN 1x4 OUT 1x1
vfloat radius(vfloat arg0)
{
    vec4 a = smear_vec4(arg0);
    float r = sqrt(a.x * a.x + a.y * a.y);
    return make_vfloat(r);
}
// JSFN polar IN 1x4 OUT 1x2
vfloat polar(vfloat arg0)
{
    float r = radius(arg0).v.x;
    float t = theta(arg0).v.x;
    return make_vfloat(r, t);
}
// JSFN height IN 1x4 OUT 1x1
vfloat height(vfloat arg0)
{
    vec4 a = smear_vec4(arg0);
    float r = a.z;
    return make_vfloat(r);
}
// JSGEN gradient z
vfloat gradient_z(vfloat pos)
{
    float epsilon = 0.0001;
    float oo_epsilon = 1.0 / epsilon;
    vfloat pos_dx = make_vfloat(pos.v.x + epsilon, pos.v.y, pos.v.z, pos.v.w);
    vfloat pos_dy = make_vfloat(pos.v.x, pos.v.y + epsilon, pos.v.z, pos.v.w);
    vfloat pos_dz = make_vfloat(pos.v.x, pos.v.y, pos.v.z + epsilon, pos.v.w);
    vfloat pos_dw = make_vfloat(pos.v.x, pos.v.y, pos.v.z, pos.v.w + epsilon);
    vfloat var1 = z(pos);
    vfloat var1_dx = z(pos_dx);
    vfloat var1_dy = z(pos_dy);
    vfloat var1_dz = z(pos_dz);
    vfloat var1_dw = z(pos_dw);
    float var0_dx = (var1_dx.v.x - var1.v.x) * oo_epsilon;
    float var0_dy = (var1_dy.v.y - var1.v.y) * oo_epsilon;
    float var0_dz = (var1_dz.v.z - var1.v.z) * oo_epsilon;
    float var0_dw = (var1_dw.v.w - var1.v.w) * oo_epsilon;
    vfloat var0 = make_vfloat(var0_dx, var0_dy, var0_dz, var0_dw);
    return var0;
}
// JSFN height_normal IN 1x4 OUT 1x3
vfloat height_normal(vfloat arg0)
{
    vfloat v = gradient_z(arg0);
    vec3 r;
    r.x = -v.v.x;
    r.y = -v.v.y;
    r.z = 1.0;
    return make_vfloat(r);
}
// JSFN hue_from_rgb IN 1x3(rgb) OUT 1x1
vfloat hue_from_rgb(vfloat arg0)
{
    vec4 a = smear_vec4(arg0);
    float r = huef(a.x, a.y, a.z);
    return make_vfloat(r);
}
// JSFN saturation_from_rgb IN 1x3(rgb) OUT 1x1
vfloat saturation_from_rgb(vfloat arg0)
{
    vec4 a = smear_vec4(arg0);
    float r = saturationf(a.x, a.y, a.z);
    return make_vfloat(r);
}
// JSFN lightness_from_rgb IN 1x3(rgb) OUT 1x1
vfloat lightness_from_rgb(vfloat arg0)
{
    vec4 a = smear_vec4(arg0);
    float r = lightnessf(a.x, a.y, a.z);
    return make_vfloat(r);
}
// JSFN red_from_hsl IN 1x3(rgb) OUT 1x1
vfloat red_from_hsl(vfloat arg0)
{
    vec4 a = smear_vec4(arg0); // FIXME get3
    float r = red_from_hslf(a.x, a.y, a.z);
    return make_vfloat(r);
}
// JSFN green_from_hsl IN 1x3(rgb) OUT 1x1
vfloat green_from_hsl(vfloat arg0)
{
    vec4 a = smear_vec4(arg0);
    float r = green_from_hslf(a.x, a.y, a.z);
    return make_vfloat(r);
}
// JSFN blue_from_hsl IN 1x3(rgb) OUT 1x1
vfloat blue_from_hsl(vfloat arg0)
{
    vec4 a = smear_vec4(arg0);
    float r = blue_from_hslf(a.x, a.y, a.z);
    return make_vfloat(r);
}
// JSFN rgb_from_hsl IN 1x3(rgb) OUT 1x3
vfloat rgb_from_hsl(vfloat arg0)
{
    vec3 a = get_vec3(arg0);
    vec3 r = rgb_from_hslf3(a);
    return make_vfloat(r);
}
// JSFN hsl_from_rgb IN 1x3(rgb) OUT 1x3
vfloat hsl_from_rgb(vfloat arg0)
{
    vec3 a = get_vec3(arg0);
    vec3 r = hsl_from_rgbf3(a);
    return make_vfloat(r);
}
// JSFN vadd IN 2x4 OUT 1x4
vfloat vadd(vfloat arg0, vfloat arg1)
{
    vec4 a = smear_vec4(arg0);
    vec4 b = smear_vec4(arg1);
    vec4 r = a + b;
    return make_vfloat(r);
}
// JSFN vsub IN 2x4 OUT 1x4
vfloat vsub(vfloat arg0, vfloat arg1)
{
    vec4 a = smear_vec4(arg0);
    vec4 b = smear_vec4(arg1);
    vec4 r = a - b;
    return make_vfloat(r);
}
// JSFN vmul IN 2x4 OUT 1x4
vfloat vmul(vfloat arg0, vfloat arg1)
{
    vec4 a = smear_vec4(arg0);
    vec4 b = smear_vec4(arg1);
    vec4 r = a * b;
    return make_vfloat(r);
}
// JSFN vdivide IN 2x4 OUT 1x4
vfloat vdivide(vfloat arg0, vfloat arg1)
{
    vec4 a = smear_vec4(arg0);
    vec4 b = smear_vec4(arg1);
    vec4 r = a / b;
    return make_vfloat(r);
}
// JSFN vmin IN 2x4 OUT 1x4
vfloat vmin(vfloat arg0, vfloat arg1)
{
    vec4 a = smear_vec4(arg0);
    vec4 b = smear_vec4(arg1);
    vec4 r = min(a,b);
    return make_vfloat(r);
}
// JSFN vmax IN 2x4 OUT 1x4
vfloat vmax(vfloat arg0, vfloat arg1)
{
    vec4 a = smear_vec4(arg0);
    vec4 b = smear_vec4(arg1);
    vec4 r = max(a,b);
    return make_vfloat(r);
}
// JSFN vmod IN 2x4 OUT 1x4
vfloat vmod(vfloat arg0, vfloat arg1)
{
    vec4 a = smear_vec4(arg0);
    vec4 b = smear_vec4(arg1);
    vec4 r = mod(a,b);
    return make_vfloat(r);
}
// JSFN vdot IN 2x4 OUT 1x1
vfloat vdot(vfloat arg0, vfloat arg1)
{
    vec4 a = get_vec4(arg0);
    vec4 b = get_vec4(arg1);
    float r = a.x * b.x + a.y * b.y + a.z * b.z + a.w * b.w;
    return make_vfloat(r);
}
// JSFN cross3 IN 2x3 OUT 1x3
vfloat cross3(vfloat arg0, vfloat arg1)
{
    vec4 a = smear_vec4(arg0);
    vec4 b = smear_vec4(arg1);
    vec4 r;
    r.x = a.y * b.z - a.z * b.y;
    r.y = a.z * b.x - a.x * b.z;
    r.z = a.x * b.y - a.y * b.x;
    r.w = 0.0;
    return make_vfloat(r);
}
// JSFN adjust_hsl IN 2x3(rgb) OUT 1x3
// (defn adjust-hsl [shift source] (rgb-from-hsl (v+ shift (hsl-from-rgb source))))
vfloat adjust_hsl(vfloat arg0, vfloat arg1)
{
    vec3 a = smear_vec3(arg0);
    vec3 b = get_vec3(arg1);
    vec3 v = rgb_from_hslf3(a + hsl_from_rgbf3(b));
    return make_vfloat(v);
}
// JSFN adjust_hue IN 2x3(rgb) OUT 1x3
// (defn adjust-hue [shift source] (rgb-from-hsl (v+ [(component shift 0) 0 0] (hsl-from-rgb source))))
vfloat adjust_hue(vfloat arg0, vfloat arg1)
{
    vec3 a = get_vec3(arg0);
    vec3 b = get_vec3(arg1);
    vec3 tmp = vec3(a.x, 0.0, 0.0);
    vec3 v = rgb_from_hslf3(tmp + hsl_from_rgbf3(b));
    return make_vfloat(v);
}
// JSFN checker(addpos) IN 3x4 OUT 1x4
vfloat checker(vfloat pos, vfloat arg0, vfloat arg1)
{
    float cond = (fract(pos.v.x) - 0.5) * (fract(pos.v.y) - 0.5);
    return vif(make_vfloat(cond), arg0, arg1);
}
// JSFN vconcat IN 2x? OUT 1x?
vfloat vconcat(vfloat arg0, vfloat arg1)
{
    int na = arg0.components;
    int nb = arg1.components;
    int out_comp = min(4, na + nb);
    vec4 r;
    // convoluted, but hopefully works?
    r.x = (na >= 1) ? arg0.v.x : arg1.v.x;
    if (na >= 2) {
        r.y = arg0.v.y;
    }
    else { // na = 0, 1
        r.y = (na == 1) ? arg1.v.x : arg1.v.y;
    }
    if (na >= 3) {
        r.z = arg0.v.z;
    }
    else { // na = 0, 1, 2
        if (na == 0) {
            r.z = arg1.v.z;
        }
        else if (na == 1) {
            r.z = arg1.v.y;
        }
        else {
            r.z = arg1.v.x;
        }
    }
    if (na == 4) {
        r.w = arg0.v.w;
    }
    else { // na = 0, 1, 2, 3
        if (na == 0) {
            r.w = arg1.v.w;
        }
        else if (na == 1) {
            r.w = arg1.v.z;
        }
        else if (na == 2) {
            r.w = arg1.v.y;
        }
        else {
            r.w = arg1.v.x;
        }
    }
    if (out_comp == 1) {
        return make_vfloat(r.x);
    } else if (out_comp == 2) {
        return make_vfloat(r.x, r.y);
    } else if (out_comp == 3) {
        return make_vfloat(r.x, r.y, r.z);
    } else if (out_comp == 4) {
        return make_vfloat(r.x, r.y, r.z, r.w);
    } else {
        return make_vfloat();
    }
}
// JSFN average IN 2x4 OUT 1x4
vfloat average(vfloat arg0, vfloat arg1)
{
    vec4 a = smear_vec4(arg0);
    vec4 b = smear_vec4(arg1);
    vec4 r;
    r.x = 0.5 * (a.x + b.x);
    r.y = 0.5 * (a.y + b.y);
    r.z = 0.5 * (a.z + b.z);
    r.w = 0.5 * (a.w + b.w);
    return make_vfloat(r);
}
// JSFN lerp IN 3x4 OUT 1x4
vfloat lerp(vfloat arg0, vfloat arg1, vfloat arg2)
{
    vec4 a = smear_vec4(arg0);
    vec4 b = smear_vec4(arg1);
    vec4 c = smear_vec4(arg2);
    vec4 r;
    r.x = a.x * b.x + (1.0 - a.x) * c.x;
    r.y = a.y * b.y + (1.0 - a.y) * c.y;
    r.z = a.z * b.z + (1.0 - a.z) * c.z;
    r.w = a.w * b.w + (1.0 - a.w) * c.w;
    return make_vfloat(r);
}
// JSFN vclamp IN 3x4 OUT 1x4
vfloat vclamp(vfloat arg0, vfloat arg1, vfloat arg2)
{
    vec4 a = smear_vec4(arg0);
    vec4 b = smear_vec4(arg1);
    vec4 c = smear_vec4(arg2);
    vec4 r = clamp(a,b,c);
    return make_vfloat(r);
}
// JSFN average IN 3x4 OUT 1x4
vfloat average(vfloat arg0, vfloat arg1, vfloat arg2)
{
    vec4 a = smear_vec4(arg0);
    vec4 b = smear_vec4(arg1);
    vec4 c = smear_vec4(arg2);
    vec4 r;
    r.x = 0.333333333333 * (a.x + b.x + c.x);
    r.y = 0.333333333333 * (a.y + b.y + c.y);
    r.z = 0.333333333333 * (a.z + b.z + c.z);
    r.w = 0.333333333333 * (a.w + b.w + c.w);
    return make_vfloat(r);
}
// JSFN vconcat IN 3x4 OUT 1x4
vfloat vconcat(vfloat arg0, vfloat arg1, vfloat arg2)
{
    return vconcat(vconcat(arg0, arg1), arg2);
}
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
// Part of WebGL translation of the Clisk Library https://github.com/mikera/clisk
// by Roger Allen for the purpose of making a transpiler.
// --------------------------------------------------------------------------------
// THREE.js main function
void main() {
  vec4 pos;
  pos.x = gl_FragCoord.x/iResolution.x;
  pos.y = 1.0 - gl_FragCoord.y/iResolution.y; // invert Y
  pos.z = 0.0;
  pos.w = iTime;

  vec2 off;
  off = uOffset/iResolution.xy;

  pos.x = uZoom*(pos.x - off.x);
  pos.y = uZoom*(pos.y - off.y);

  gl_FragColor = smear_vec4(pixel_fn0(make_vfloat(pos)));
  gl_FragColor.w = 1.0;
}
