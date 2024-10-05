
#version 330
// fragment: fluid show
// displays fluid velocity based on temperature

in vec2 g_uv;

out vec4 fragColor;

void main() {
    fragColor = vec4(2, 2, 2, 0.02*(1-g_uv.x));
}

