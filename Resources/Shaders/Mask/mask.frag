
#version 150 core
in vec4 vertex_colors;
in vec3 texture_coords;
out vec4 final_colors;

uniform sampler2D sprite_texture;

uniform float iTime;

#define MASK 0.9
#define TIME 1.2


float easeOutBounce(float x) {
    const float n1 = 7.5625;
    const float d1 = 2.75;

    if (x < 1 / d1) {
        return n1 * x * x;
    } else if (x < 2 / d1) {
        return n1 * (x -= 1.5 / d1) * x + 0.75;
    } else if (x < 2.5 / d1) {
        return n1 * (x -= 2.25 / d1) * x + 0.9375;
    } else {
        return n1 * (x -= 2.625 / d1) * x + 0.984375;
    }
}


void main() {
    float b = easeOutBounce(min(1, iTime / TIME));

    if (texture_coords.x < b) {
        col = vec4(0, 0, 0, MASK);
    }
}