
#version 330
// fragment: blur
//offsets color based on position

uniform sampler2D texture0;
uniform float width;

in vec2 uv;

out vec4 fragColor;

void main() {
    float disp = 1+2*width;
    fragColor = vec4(texture(texture0, uv*vec2(1+width, 1+width)-0.5*vec2(width, width)).x, texture(texture0, uv*vec2(1+2*width, 1)-vec2(width, 0)).y, texture(texture0, uv*vec2(1, 1+2*width)-vec2(0, width)).z, 1.0);
}
