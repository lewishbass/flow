
#version 330
// fragment: pressure sim
// calculates the total flow out of the cell

uniform sampler2D texture0; // fluid state

in vec2 uv;

out vec4 fragColor;

void main(){
    ivec2 pos = ivec2(gl_FragCoord.xy);// fluid infrom from cell
    vec4 fc = texelFetch(texture0, pos+ivec2(0, 0), 0); // current
    vec4 fu = texelFetch(texture0, pos+ivec2(0, 1), 0); // up
    vec4 fl = texelFetch(texture0, pos+ivec2(1, 0), 0); // left
    float d = fl.x-fc.x+fu.y-fc.y; // divergence
    fragColor = vec4(d, d, d, 1.0);
}

