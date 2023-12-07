from Crash import *


slice_frag_source = """
#version 150 core
in vec4 vertex_colors;
in vec3 texture_coords;
out vec4 fragColor;

in vec2 s;

uniform sampler2D sprite_texture;

uniform ivec4 bounds = ivec4(0, 0, 0, 0);

// 0 = tile
// 1 = stretch
uniform int mode = 0;


vec2 uvSlice(vec2 uv, vec4 b) {
    if (mode == 1) {
        vec2 t = clamp((s * uv - b.xy) / (s - b.xy - b.zw), 0.0, 1.0);
        return mix(uv * s, 1.0 - s * (1.0 - uv), t);
    }
    else {
        vec2 o = min(vec2(1.0, 1.0), floor(s * uv / b.xy));
        vec2 m = mod(s * uv - b.xy, 1 - (b.xy + b.zw)) + b.xy;
        vec2 g = mix(s * uv, m, o);

        vec2 k = min(vec2(1.0, 1.0), floor(s * uv / (s - b.zw)));
        return mix(g, 1.0 - s * (1.0 - uv), k);
    }
}


void main() {
    ivec2 size = textureSize(sprite_texture, 0);

    vec4 b = float(bounds) / size.xyxy;
    vec2 uv = uvSlice(texture_coords.xy, b);

    fragColor = texture(sprite_texture, uv) * vertex_colors;
}
"""

slice_vert_source = """
#version 150 core
in vec3 translate;
in vec4 colors;
in vec3 tex_coords;
in vec2 scale;
in vec3 position;
in float rotation;

out vec2 s;

out vec4 vertex_colors;
out vec3 texture_coords;

uniform WindowBlock
{
    mat4 projection;
    mat4 view;
} window;

mat4 m_scale = mat4(1.0);
mat4 m_rotation = mat4(1.0);
mat4 m_translate = mat4(1.0);

void main()
{
    m_scale[0][0] = scale.x;
    m_scale[1][1] = scale.y;
    m_translate[3][0] = translate.x;
    m_translate[3][1] = translate.y;
    m_translate[3][2] = translate.z;
    m_rotation[0][0] =  cos(-radians(rotation));
    m_rotation[0][1] =  sin(-radians(rotation));
    m_rotation[1][0] = -sin(-radians(rotation));
    m_rotation[1][1] =  cos(-radians(rotation));

    gl_Position = window.projection * window.view * m_translate * m_rotation * m_scale * vec4(position, 1.0);

    vertex_colors = colors;
    texture_coords = tex_coords;

    s = scale;
}
"""


class SlicedSprite(Sprite):
    def __init__(self, img, group=0, batch="default", ppu=Screen.unit):
        frag = pyglet.graphics.shader.Shader(slice_frag_source, "fragment")
        vert = pyglet.graphics.shader.Shader(slice_vert_source, "vertex")

        shader = pyglet.graphics.shader.ShaderProgram(frag, vert)

        self._bounds = [0, 0, 0, 0]

        super().__init__(img, group=group, batch=batch, program=shader, ppu=ppu)

    @property
    def bounds(self):
        return self._bounds

    @bounds.setter
    def bounds(self, value):
        self._bounds = [value[0], value[1], value[2], value[3]]
        self.program["bounds"] = self.bounds

