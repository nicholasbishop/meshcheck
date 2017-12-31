#version 410

layout(triangles) in;
layout(triangle_strip, max_vertices = 3) out;
out vec3 geom_normal;
out vec3 geom_distance;

void main()
{
  vec3 A = vec3(gl_in[2].gl_Position - gl_in[0].gl_Position);
  vec3 B = vec3(gl_in[1].gl_Position - gl_in[0].gl_Position);
  geom_normal = normalize(cross(A, B));
    
  geom_distance = vec3(1, 0, 0);
  gl_Position = gl_in[0].gl_Position; EmitVertex();

  geom_distance = vec3(0, 1, 0);
  gl_Position = gl_in[1].gl_Position; EmitVertex();

  geom_distance = vec3(0, 0, 1);
  gl_Position = gl_in[2].gl_Position; EmitVertex();

  EndPrimitive();
}
