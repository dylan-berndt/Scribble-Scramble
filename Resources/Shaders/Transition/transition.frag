

#version 150 core
in vec4 vertex_colors;
in vec3 texture_coords;
out vec4 fragCoord;

#define PIXEL_SIZE 4.0

#define OFFSET 5
#define CIRCLE_SIZE 20

uniform float iTime = -1;
uniform bool in_out = true;

uniform sampler2D sprite_texture;

vec2 pixel_num(in vec2 position)
{
    return floor(position / PIXEL_SIZE);
}

void main()
{
    float transparency;

    vec2 size = textureSize(sprite_texture, 0);
    vec2 n = pixel_num(texture_coords.xy * size);
    vec2 p = n * PIXEL_SIZE;

    int ym = int(n.x) / CIRCLE_SIZE;

    int x = int(n.x) % CIRCLE_SIZE;
    int y = (int(n.y) + (ym * OFFSET)) % CIRCLE_SIZE;

    vec2 centered = vec2(x, y) - vec2(CIRCLE_SIZE / 2, CIRCLE_SIZE / 2);

    float d = distance(centered, vec2(0, 0));

    float s = (1.0 + (1.0 - iTime * 2.0) - p.x / size.x) * float(CIRCLE_SIZE);

    if (!in_out) {
        d = CIRCLE_SIZE - d;
    }

    if (d > s && in_out) {
        transparency = 0;
    }
    else if (d < s && !in_out) {
        transparency = 0;
    }
    else {
        transparency = 1;
    }

    vec4 frag = vec4(0, 0, 0, transparency);

    fragCoord = frag * texture(sprite_texture, texture_coords.xy) * vertex_colors;
}