#version 330 core
layout (points) in;
layout (triangle_strip, max_vertices = 4) out;

uniform float iTime;

in VS_OUT {
    vec4 color;
} gs_in[];

out vec4 fColor;

#define LIFETIME 0.4
#define SIZE 0.1

void main() {
    float f = SIZE;
//   f = SIZE * (LIFETIME - mod(iTime, LIFETIME));

    fColor = gs_in[0].color;

    gl_Position = gl_in[0].gl_Position + vec4(-f,-f, 0.0, 0.0);
    EmitVertex();

    gl_Position = gl_in[0].gl_Position + vec4( f,-f, 0.0, 0.0);
    EmitVertex();

    gl_Position = gl_in[0].gl_Position + vec4(-f, f, 0.0, 0.0);
    EmitVertex();

    gl_Position = gl_in[0].gl_Position + vec4( f, f, 0.0, 0.0);
    EmitVertex();

    EndPrimitive();
}