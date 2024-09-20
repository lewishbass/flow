
#version 330
// fragment: blur
// simple vertical gaussian blur
// and film grain

uniform sampler2D texture0;
uniform float width;
uniform float dx;
uniform float dy;
uniform float resolution;
uniform float time;

in vec2 uv;

out vec4 fragColor;

void main() {
    vec3 color = texture(texture0, uv+vec2(0, 0)*1).xyz;
    
    for(float i = -width; i < width; i+=resolution){//quick and dirty gaussian blur
        float gauss = (0.6/(0.6+3/width*i*i))*0.2*resolution/width;
        color += texture(texture0, vec2(uv.x+i*dx, uv.y+i*dy)).xyz*gauss;
        color += texture(texture0, vec2(uv.x+i*dy, uv.y-i*dx)).xyz*gauss;
    }

    float rand = fract(pow(3.234+(floor(uv.x*500)/500)*163.234, 2.54+0.3*fract((floor(uv.y*500)/500)*30.43+time)));//this makes good noise, dont ask how
    color *= (1-0.05*rand);
    color -= 0.02*vec3(rand, rand, rand);

    float l = dot(color, vec3(0.21, 0.71, 0.07));//color grading
    vec3 tc = color / (color + 1.0);
    fragColor = vec4(mix(color / (l + 1.0), tc, tc), 1.0);
}
