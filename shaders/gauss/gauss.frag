
#version 330
// fragment: gauss sim
// attempts to balance the flow out of the cell to 0

uniform sampler2D texture0; // fluid state
uniform sampler2D texture1; // calculated divergence
uniform sampler2D texture2; // input
uniform float over; // over relaxation

in vec2 uv;

out vec4 fragColor;

void main(){
    ivec2 pos = ivec2(gl_FragCoord.xy);// fluid infrom from cell
    vec4 dc = texelFetch(texture1, pos+ivec2(0, 0), 0); // current
    vec4 dd = texelFetch(texture1, pos-ivec2(0, 1), 0); // down
    vec4 dr = texelFetch(texture1, pos-ivec2(1, 0), 0); // right
    vec4 state = texelFetch(texture0, pos, 0);
    vec4 smoke = texelFetch(texture2, pos, 0);
    // balance divergence to 0
    fragColor = vec4(state.x+(dc.x/4.0-dr.x/4.0)*over, state.y+(dc.x/4.0-dd.x/4.0)*over + state.z*0.002, max(state.z, smoke.x), 1.0);
}

