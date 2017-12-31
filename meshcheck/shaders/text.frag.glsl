#version 330

in vec2 vert_uv;
out vec4 frag_color;
uniform sampler2D text;

void main() {
  frag_color = texture(text, vert_uv);
}
