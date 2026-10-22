$input a_position, a_normal, a_texcoord0, a_tangent, a_bitangent, i_data0, i_data1, i_data2, i_data3
$output v_worldPos, v_normal, v_tangent, v_bitangent, v_texcoord0, v_viewPos, v_objectPos, v_objectNormal

// Generated from Assets/ShaderGraphs/LaunchNight/Lightning.shadergraph by the shader graph compiler: edit the graph, not this file.
#define SG_TRANSPARENT 1
#define SG_FOG 1

#include "Common.sh"
#if SG_SKINNED
#include "Skinning.sh"
#endif
#include "ShaderGraph/SGLib.sh"

uniform vec4 u_sgParams[16];
// u_sgParams[0]: Bolt Color (Vector 3)
// u_sgParams[1]: Intensity (Float)
// u_sgParams[2]: Seed (Float)

void sgCustom_Bolt_21744(vec2 UV, float Time, float Seed, out float Glow)
{
float y = UV.y;
float path = 0.0;
float amp = 0.16;
float freq = 3.0;
for (int i = 0; i < 5; i++)
{
    float fi = float(i);
    float k = y * freq + Seed * (fi + 1.0) * 1.7;
    float a = fract(sin(floor(k) * 12.9898 + fi * 4.1 + Seed) * 43758.5453) - 0.5;
    float b = fract(sin((floor(k) + 1.0) * 12.9898 + fi * 4.1 + Seed) * 43758.5453) - 0.5;
    path += mix(a, b, fract(k)) * amp;
    amp *= 0.5;
    freq *= 2.3;
}
float d = abs(UV.x - 0.5 - path);
float branchY = clamp((y - 0.35) / 0.3, 0.0, 1.0);
float branch = abs(UV.x - 0.5 - path - branchY * 0.12 - sin(y * 47.0 + Seed) * 0.01);
branch = (1.0 - smoothstep(0.0, 0.004, branch)) * step(0.35, y) * step(y, 0.65) * (1.0 - branchY);
float core = 1.0 - smoothstep(0.0, 0.005, d);
float halo = exp(-d * 45.0) * 0.45;
float ends = smoothstep(0.0, 0.04, y) * smoothstep(1.0, 0.94, y);
float flick = 0.55 + 0.45 * step(0.4, fract(Time * 19.0));
Glow = (core + halo + branch) * ends * flick;
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
