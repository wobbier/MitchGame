$input a_position, a_normal, a_texcoord0, a_tangent, a_bitangent, i_data0, i_data1, i_data2, i_data3, a_indices, a_weight
$output v_worldPos, v_normal, v_tangent, v_bitangent, v_texcoord0, v_viewPos, v_objectPos, v_objectNormal

// Generated from Assets/ShaderGraphs/LaunchNight/RainGlass.shadergraph by the shader graph compiler: edit the graph, not this file.
#define SG_TRANSPARENT 1
#define SG_SKINNED 1

#include "Common.sh"
#if SG_SKINNED
#include "Skinning.sh"
#endif
#include "ShaderGraph/SGLib.sh"

uniform vec4 u_sgParams[16];
// u_sgParams[0]: Tint (Vector 3)
// u_sgParams[1]: Scale (Float)
// u_sgParams[2]: Opacity (Float)
// u_sgParams[3]: Drop Glint (Vector 3)

void sgCustom_RainDrops_95161(vec2 P, float Time, float Scale, out float Height)
{
vec2 p = P * Scale;
float h = 0.0;
{
    vec2 uv = p * 22.0;
    vec2 id = floor(uv);
    vec2 fp = fract(uv) - vec2_splat(0.5);
    float n = fract(sin(dot(id, vec2(12.9898, 78.233))) * 43758.5453);
    vec2 o = vec2(fract(n * 13.1), fract(n * 71.7)) - vec2_splat(0.5);
    float r = 0.1 + 0.16 * fract(n * 7.3);
    float life = fract(Time * (0.05 + 0.1 * fract(n * 3.7)) + n);
    float d = length(fp - o * 0.5);
    h = max(h, (1.0 - smoothstep(r * 0.4, r, d)) * step(0.72, n) * smoothstep(1.0, 0.7, life));
}
{
    float cw = 0.16;
    float colx = floor(p.x / cw);
    float n = fract(sin(colx * 78.233 + 1.3) * 43758.5453);
    float x = (fract(p.x / cw) - 0.5) * cw + sin(p.y * 6.0 + n * 6.28) * 0.012;
    float s = p.y / 0.9 + Time * (0.18 + 0.3 * n) + n * 7.0;
    float cycle = floor(s);
    float dy = (fract(s) - 0.5) * 0.9;
    float m = fract(sin((cycle + colx * 13.0) * 12.9898) * 43758.5453);
    float head = 1.0 - smoothstep(0.008, 0.016, length(vec2(x, dy * 0.75)));
    float trailMask = step(0.0, dy) * (1.0 - smoothstep(0.0, 0.32, dy));
    float trail = (1.0 - smoothstep(0.002, 0.005, abs(x))) * trailMask;
    float bead = fract(dy * 26.0);
    float beads = (1.0 - smoothstep(0.003, 0.007, length(vec2(x, (bead - 0.5) / 26.0)))) * trailMask * step(0.45, fract(sin(floor(dy * 26.0) + m * 40.0) * 917.3));
    h = max(h, (head + max(trail * 0.35, beads * 0.8)) * step(0.3, m));
}
Height = h;
}


void main()
{
	// Instanced: the model matrix comes from the instance buffer (and the bone palette when skinned).
	mat4 sg_model = mtxFromCols(i_data0, i_data1, i_data2, i_data3);
#if SG_SKINNED
	sg_model = mul(sg_model, skinMatrix(a_indices, a_weight));
#endif
	mat3 sg_normalMatrix = cofactor(sg_model);


	// Outputs
	vec3 sgOut_PositionOffset = vec3(0.0, 0.0, 0.0);

	vec3 objectPos = a_position;
#if SG_OFFSET_WORLD
	vec3 worldPos = mul(sg_model, vec4(a_position, 1.0)).xyz + sgOut_PositionOffset;
#else
	objectPos += sgOut_PositionOffset;
	vec3 worldPos = mul(sg_model, vec4(objectPos, 1.0)).xyz;
#endif
	gl_Position = mul(u_viewProj, vec4(worldPos, 1.0));

	v_normal = mul(sg_normalMatrix, a_normal);
	v_tangent = mul(sg_model, vec4(a_tangent, 0.0)).xyz;
	v_bitangent = mul(sg_model, vec4(a_bitangent, 0.0)).xyz;
	v_worldPos = worldPos;
	v_viewPos = mul(u_view, vec4(worldPos, 1.0));
	v_texcoord0 = a_texcoord0;
	v_objectPos = objectPos;
	v_objectNormal = a_normal;
}
