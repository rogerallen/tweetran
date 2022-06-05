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
