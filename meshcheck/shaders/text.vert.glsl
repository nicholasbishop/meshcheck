#version 330

in vec2 pos;
in vec2 uv;
out vec2 vert_uv;
uniform mat4 proj;
uniform mat4 model_view;
uniform vec2 size;

void main() {
  vert_uv = uv;
  vec2 scaled_size = size * 0.01;
  vec2 offset_pos = pos - 0.5;
  mat4 billboard = model_view;
  for (int i = 0; i < 3; i++) {
    for (int j = 0; j < 3; j++) {
      billboard[i][j] = i == j ? 1 : 0;
    }
  }
  float z_offset = 0.5;
  mat4 transform = proj * billboard;
  gl_Position = transform * vec4(offset_pos * scaled_size, z_offset, 1.0);
}
