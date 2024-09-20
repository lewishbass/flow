
#version 330
// fragment: advection sim
// moves liquid in grid according to velocity

uniform sampler2D texture0; // fluid state
uniform float speed;

in vec2 uv;

out vec4 fragColor;

void main(){
    ivec2 pos = ivec2(gl_FragCoord.xy);// fluid infrom from cell
    vec4 vel = vec4(0, 0, 0, 0);
    vel += texelFetch(texture0, pos+ivec2( 0,  0), 0);
    vel += texelFetch(texture0, pos+ivec2( 1,  0), 0);
    vel += texelFetch(texture0, pos+ivec2( 0,  1), 0);
    vec4 fc = texelFetch(texture0, pos, 0); // current
    
    vec4 ocol = texelFetch(texture0, pos, 0);

    ivec2 npos = pos-ivec2(floor(vel.x*speed), floor(vel.y*speed)); // update
    vec2 posfrac = vec2(fract(vel.x*speed), fract( vel.y*speed)); // get fractional part of position
    vec4 ncol = vec4(0, 0, 0, 0); // interpolate pixels based on landing position
    ncol += texelFetch(texture0, npos-ivec2( 0,  0), 0)*(1-posfrac.x)*(1-posfrac.y);
    ncol += texelFetch(texture0, npos-ivec2( 1,  0), 0)*(  posfrac.x)*(1-posfrac.y);
    ncol += texelFetch(texture0, npos-ivec2( 0,  1), 0)*(1-posfrac.x)*(  posfrac.y);
    ncol += texelFetch(texture0, npos-ivec2( 1,  1), 0)*(  posfrac.x)*(  posfrac.y);

    fragColor = vec4(ncol.xyz, 1.0);
}

