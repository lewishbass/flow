
#version 330
//   vertex: gauss sim

in vec2 in_vert;
in vec2 in_uv;
out vec2 uv;

void main() {
    gl_Position = vec4(in_vert, 0.0, 1.0);
    uv = in_uv;
}
