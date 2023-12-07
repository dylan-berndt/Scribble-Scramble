
#version 150 core
in vec4 vertex_colors;
in vec3 texture_coords;
out vec4 final_colors;

#define PIXEL_SIZE 4.0

uniform sampler2D sprite_texture;

vec2 pixel_pos(vec2 in_pos) {
    return floor(in_pos / PIXEL_SIZE) * PIXEL_SIZE;
}

void main() {
    ivec2 size = textureSize(sprite_texture, 0);
    vec2 n = pixel_pos(texture_coords.xy * size);
    n = n / size;

    vec4 col = texture(sprite_texture, n);

    bool near = false;
    for (int i = 0; i < 4; i++) {
        vec2 s = PIXEL_SIZE * (floor(i / 2.0) * 2 - 1) * vec2(i % 2, (i + 1) % 2) / size;
        vec4 sam = texture(sprite_texture, n + s);
        if (sam.a == 1) {
            near = true;
        }
    }
    if (near && col.a < 1) {
        col = vec4(0, 0, 0, 1);
    }
    else if (col.a < 1) {
        col = vec4(0, 0, 0, 0);
    }

    final_colors = col * vertex_colors;
}