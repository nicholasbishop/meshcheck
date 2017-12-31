#version 330

uniform mat4 mvp;
in vec3 vert;

void main() {
  gl_Position = mvp * vec4(vert, 1.0);
}
