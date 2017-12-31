#version 330

in vec3 pos;
out vec3 vert_pos;
uniform mat4 mvp;

void main()
{
  gl_Position = mvp * vec4(pos, 1.0);
}
