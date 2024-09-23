
#version 330
//   vertex: fluid show

in vec4 in_vert;
in vec2 in_uv;
in vec4 in_color;

out vec2 uv;
out vec4 vertex_color;

void main() {
    gl_Position = vec4(in_vert);
    uv = in_uv;
    vertex_color = in_color;
}
