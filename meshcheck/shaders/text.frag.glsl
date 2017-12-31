#version 330

in vec2 vert_uv;
out vec4 frag_color;
uniform sampler2D text;

void main() {
  vec4 tex = texture(text, vert_uv);
  frag_color.rgb = tex.rrr;
  frag_color.a = 1.0;
}
