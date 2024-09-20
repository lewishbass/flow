
#version 330
// fragment: fluid show
// displays fluid velocity based on temperature

uniform sampler2D texture0;

in vec2 uv;

out vec4 fragColor;

void main() {
    vec4 col = texture(texture0, uv);
    fragColor = vec4(col.z*abs(col.x)*3, col.z*abs(col.y), col.z*1.75, 1.0);
}

