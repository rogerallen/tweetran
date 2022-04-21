// --------------------------------------------------------------------------------
// ShaderToy main function
void mainImage( out vec4 fragColor, in vec2 fragCoord )
{
    vec4 pos;
    pos.x = gl_FragCoord.x/iResolution.x;
    pos.y = 1.0 - gl_FragCoord.y/iResolution.y; // invert Y
    pos.z = 0.0;
    pos.w = iTime;

    // Output to screen
    fragColor = get_vec4(pixel_fn0(make_vfloat(pos)));
}