#version 150 core

#define PI 3.14159

#define COLUMNS 10
#define ROWS 5

#define STRENGTH 0.24
#define DIRECTION vec2(-1, -0.4)
#define SPEED 1.0

uniform sampler2D sprite_texture;
uniform float iTime = 0;

in vec3 texture_coords;
in vec4 vertex_colors;
out vec4 fragColor;

float rand(vec2 co){
    return fract(sin(dot(co.xy ,vec2(12.9898,78.233))) * 43758.5453);
}

float worley(vec2 position) {
    int px = int(floor(position.x * ROWS));
    int py = int(floor(position.y * COLUMNS));

    float min_dist = 1000.0;

    for (int y = -2; y < 3; y++) {
        for (int x = -2; x < 3; x++) {
            int ix = px + x;
            int iy = py + y;

            float angle = 2 * PI * rand(vec2(ix, iy)) + iTime * SPEED;

            vec2 center = vec2(cos(angle), sin(angle)) * 0.4 + vec2(ix, iy);

            float d = distance(position, center / vec2(ROWS, COLUMNS));

            min_dist = min(d, min_dist);
        }
    }

    return min_dist * STRENGTH * (1 - position.y);
}

void main() {
    float offset = worley(texture_coords.xy);

    vec2 tex_offset = DIRECTION * offset;

    fragColor = texture(sprite_texture, texture_coords.xy + tex_offset) * vertex_colors;
}
