
#version 330

layout (points) in;
layout (line_strip, max_vertices = 101) out;

uniform Projection {
    uniform mat4 matrix;
} proj;

uniform sampler2D texture0;
uniform float speed;
uniform int length;
uniform int skip;

in vec3 vertex_pos[];

out vec2 g_uv;
out vec3 g_color;

void main(){
    vec2 center = gl_in[0].gl_Position.xy;
    vec2 hsize = vec2(1, 1)*10;

    g_color = vec3(1, 0, 1);

    gl_Position = proj.matrix*vec4(center, vertex_pos[0].z, 1.0);
    g_uv = vec2(0, 0);
    EmitVertex();

    for(int i = 0; i < length*skip; i++){
        ivec2 center_int = ivec2(floor(center));
        vec2 center_fract = center-center_int;
        vec2 flow = vec2(0, 0);
        flow += texelFetch(texture0, center_int-ivec2(0, 0), 0).xy*(1-center_fract.x)*(1-center_fract.y);
        flow += texelFetch(texture0, center_int-ivec2(1, 0), 0).xy*(  center_fract.x)*(1-center_fract.y);
        flow += texelFetch(texture0, center_int-ivec2(0, 1), 0).xy*(1-center_fract.x)*(  center_fract.y);
        flow += texelFetch(texture0, center_int-ivec2(1, 1), 0).xy*(  center_fract.x)*(  center_fract.y);


        center = center + flow*speed/skip;
        
        if(mod(i+1, skip) == 0){
            gl_Position = proj.matrix*vec4(center, vertex_pos[0].z, 1.0);
            g_uv = vec2(float(i)/float(length*skip), 0);
            EmitVertex();
        }
    }
    
    EndPrimitive();
    
    /*gl_Position = proj.matrix*vec4(vec2( hsize.x,  hsize.y)+center, vertex_pos[0].z, 1.0);
    g_uv = vec2(1, 1);
    EmitVertex();

    gl_Position = proj.matrix*vec4(vec2( hsize.x, -hsize.y)+center, vertex_pos[0].z, 1.0);
    g_uv = vec2(1, 0);
    EmitVertex();

    EndPrimitive();*/
}