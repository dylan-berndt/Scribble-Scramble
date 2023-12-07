#version 150 core

#define PIXEL_SIZE 4.0

uniform int WATER_HEIGHT = 120;

#define PUSH_WEIGHT 0.005

#define PI 3.14159

#define COLUMNS 10
#define ROWS 30

#define SPEED 1.5

uniform sampler2D velocity;
uniform float iTime;
uniform float s;

in vec3 texture_coords;
in vec4 vertex_colors;
out vec4 fragColor;

vec3[7] PALETTE = vec3[](
vec3(50, 51, 83),
vec3(72, 74, 119),
vec3(77, 101, 180),
vec3(77, 155, 230),
vec3(143, 248, 246),
vec3(255, 255, 255),
vec3(199, 220, 208));

float rand(vec2 co){
    return fract(sin(dot(co.xy ,vec2(12.9898,78.233))) * 43758.5453);
}

float worley(vec2 position) {
    vec2 cell = floor(position * vec2(COLUMNS, ROWS));

    float min_dist = 1000.0;

    for (int y = -2; y < 3; y++) {
        for (int x = -2; x < 3; x++) {
            vec2 i = cell + vec2(x, y);

            float angle = rand(i) * 2.0 * PI + iTime * SPEED;

            vec2 center = vec2(cos(angle), sin(angle)) * 0.4;

            vec2 transform = center + i;

            float d = distance(position * vec2(COLUMNS, ROWS), transform);

            min_dist = min(min_dist, d);
        }
    }

    return min_dist;
}

int sample_height(vec2 sample_position, vec2 size) {
    int height = WATER_HEIGHT;

    float push = PUSH_WEIGHT;
    vec2 sample_texture = vec2(sample_position.x, WATER_HEIGHT * PIXEL_SIZE) / size;
    int iterations = 0;

    while(texture(velocity, sample_texture).x > push) {
        height -= 1;
        push += PUSH_WEIGHT * (1 + iterations);
        sample_texture += vec2(0, PIXEL_SIZE / size.y);
        iterations += 1;
    }

    height += int(3 * sin(-iTime * 2 + 6 * sample_position.x / size.x) +
    2 * cos(-iTime / 4.0 + 4 * sample_position.x / size.x));

    return height;
}

void main() {
    vec2 size = textureSize(velocity, 0) * s;

    vec2 pixel = floor(texture_coords.xy * size / PIXEL_SIZE) * int(PIXEL_SIZE);

    int height = sample_height(pixel, size);

    float current = int(pixel.y / PIXEL_SIZE);

    if (current < height - 1) {
        float turbulence = ((current / WATER_HEIGHT) + 0.5) * 0.5;
        turbulence += worley(pixel / size - vec2(iTime / 4.0, 0)) * 0.25;
        turbulence += min(0.2, texture(velocity, pixel / size).x);

        turbulence = pow(turbulence, 2.0);

        int num = int((pixel.x + pixel.y) / PIXEL_SIZE);

        turbulence = min(6.0 / 7.0, turbulence);

        if (num % 2 == 0) {
            turbulence -= 0.02;
        }
        else if (num % 2 == 1) {
            turbulence += 0.02;
        }

        int index = max(0, min(6, int(turbulence * 7)));

        vec3 color = PALETTE[index] / 255;

        fragColor = vec4(color, 1.0) * vertex_colors;
    }
    else if (current < height) {
        fragColor = vec4(0, 0, 0, 1);
    }
    else {
        fragColor = vec4(0, 0, 0, 0);
//        fragColor = texture(velocity, texture_coords.xy);
    }
}
