
#version 330
// fragment: fluid show
// displays fluid velocity based on temperature

uniform sampler2D texture0;

in vec2 uv;

out vec4 fragColor;

void main() {
    vec4 col = texture(texture0, uv);
    fragColor = vec4(abs(col.x)*5, abs(col.y)*1.5, 1.75, 2*col.z);
}

