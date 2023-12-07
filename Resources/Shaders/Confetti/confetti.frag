
#version 150 core
in vec4 vertex_colors;
in vec3 texture_coords;
out vec4 final_colors;

uniform sampler2D sprite_texture;

uniform float iTime;


#define PIXEL_SIZE 4.0
#define OUTLINE true

#define CIRCLE_SIZE 65.0
#define NUM_CIRCLES 60

#define PI 3.14159

#define MASK 0.9

#define DELAY 1.2
#define SPRAY_TIME 1.5
#define LIFE_TIME 1.5
#define RUN_TIME 6.0

#define ACCELERATION -6.0
#define VELOCITY 5.0

#define START_X 0.0
#define START_Y 1.2

#define VEL_SPREAD 0.3

#define TIME_SCALING 4.0


#define PALETTE_LENGTH 7

vec4 palette[PALETTE_LENGTH] = vec4[](
vec4(1, 0, 0, 1),
vec4(0, 1, 0, 1),
vec4(0, 1, 1, 1),
vec4(1, 0, 1, 1),
vec4(0, 0, 1, 1),
vec4(1, 1, 0, 1),
vec4(1, 1, 1, 1)
);

vec2 directions[9] = vec2[](
vec2(PIXEL_SIZE, 0), vec2(0, PIXEL_SIZE),
vec2(-PIXEL_SIZE, 0), vec2(0, -PIXEL_SIZE),
vec2(-PIXEL_SIZE * 2, 0), vec2(0, PIXEL_SIZE * 2),
vec2(-PIXEL_SIZE * 2, PIXEL_SIZE), vec2(-PIXEL_SIZE, PIXEL_SIZE * 2),
vec2(-PIXEL_SIZE, PIXEL_SIZE));

float det(vec2 p1, vec2 p2) {
    return p1.x * p2.y - p1.y * p2.x;
}


float c(float x) {
    x = mod(x + PI, 2 * PI) - PI;
    return 1 - (x * x) / 2;
}

float s(float x) {
    x = mod(x + PI, 2 * PI) - PI;
    return x - (x * x * x) / (3 * 2);
}


float rand(vec2 co){
    return fract(s(dot(co.xy ,vec2(12.9898,78.233))) * 43758.5453);
}


vec2 iV(int i) {
    vec2 v = vec2(VELOCITY, VELOCITY);
    v *= vec2(rand(vec2(i, i)), -rand(vec2(i * 10, i)));
    return v;
}


vec2 getPos(float time, int i) {
    time = time / TIME_SCALING;

    bool left = (i % 2) == 0;

    vec2 pos;

    vec2 v = iV(i);

    float t = time;

    float m = 1 - pow(1 - t, 5);
    if (t > 1) {
        m = 1;
    }
    m *= 0.2;

    if (left) {
        pos = vec2(0.0 - START_X, START_Y);
        float a = ACCELERATION * t * t;
        vec2 change = v * m + vec2(0, a);
        pos += change;
    }
    else {
        pos = vec2(1.0 + START_X, START_Y);
        float a = ACCELERATION * t * t;
        vec2 change = v * m * vec2(-1, 1) + vec2(0, a);
        pos += change;
    }
    return pos * textureSize(sprite_texture, 0);
}


bool circleIntersection(vec2 frag, vec2 center, int i, float time) {
    vec2 off = frag - center;
    float size = 1 - (time / LIFE_TIME);
    size = size * size;
    if (size * CIRCLE_SIZE * 2 < 0.5) {
        return false;
    }
    return size * CIRCLE_SIZE * CIRCLE_SIZE > off.x * off.x + off.y * off.y;
}


void main()
{
    vec4 col = vec4(0, 0, 0, 0);

    vec2 uv = floor(texture_coords.xy * textureSize(sprite_texture, 0) / PIXEL_SIZE) * PIXEL_SIZE;

    float t = iTime;

    if (t > DELAY) {
        for (int i = 0; i < NUM_CIRCLES; i++) {
            float timeOffset = rand(vec2(i * 10, i * 10)) * SPRAY_TIME;

            if (0 > t - DELAY - timeOffset || t - DELAY - timeOffset > RUN_TIME) {
                continue;
            }

            float m = mod(t - DELAY - timeOffset, LIFE_TIME);
            vec2 pos = getPos(m, i);

            if (circleIntersection(uv, pos, i, m)) {
                col = palette[i % PALETTE_LENGTH];
            }
            else if (OUTLINE) {
                for (int d = 0; d < 9; d++) {
                    if (circleIntersection(uv + directions[d], pos, i, m)) {
                        col = vec4(0, 0, 0, 1);
                    }
                }
            }
        }
    }

    final_colors = col * vertex_colors;
}