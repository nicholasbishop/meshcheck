#version 410

out vec4 frag_color;
in vec3 geom_normal;
in vec3 geom_distance;

// http://codeflow.org/entries/2012/aug/02/easy-wireframe-display-with-barycentric-coordinates/
float edgeFactor() {
    vec3 d = fwidth(geom_distance);
    vec3 a3 = smoothstep(vec3(0.0), d*1.5, geom_distance);
    return min(min(a3.x, a3.y), a3.z);
}

void main()
{
    vec3 color = mix(vec3(0.0), vec3(0.5), edgeFactor());
    color *= vec3(1.0) - geom_normal;
    frag_color = vec4(color, 1.0);
}
