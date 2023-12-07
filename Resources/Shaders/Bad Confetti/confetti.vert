#version 330 core

in vec2 position;
in vec4 colors;

out VS_OUT {
    vec4 color;
} vs_out;

uniform float iTime;

void main() {
    gl_Position = vec4(position, 0.0, 0.0);
    vs_out.color = colors;
}