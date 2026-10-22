$input a_position, a_normal, a_texcoord0, a_tangent, a_bitangent, i_data0, i_data1, i_data2, i_data3
$output v_worldPos, v_normal, v_tangent, v_bitangent, v_texcoord0, v_viewPos, v_objectPos, v_objectNormal

// Generated from Assets/ShaderGraphs/LaunchNight/ServerLEDs.shadergraph by the shader graph compiler: edit the graph, not this file.

#include "Common.sh"
#if SG_SKINNED
#include "Skinning.sh"
#endif
#include "ShaderGraph/SGLib.sh"

uniform vec4 u_sgParams[16];
// u_sgParams[0]: Seed (Float)
// u_sgParams[1]: Alarm (Float)
// u_sgParams[2]: Intensity (Float)

void sgCustom_Leds_73454(vec2 UV, float Time, float Seed, float Alarm, out vec3 Color)
{
vec2 grid = vec2(6.0, 44.0);
vec2 gp = UV * grid;
vec2 cell = floor(gp);
vec2 fp = fract(gp) - vec2_splat(0.5);
float h = fract(sin(dot(cell + vec2_splat(Seed * 17.0), vec2(12.9898, 78.233))) * 43758.5453);
float h2 = fract(h * 91.7);
float rate = 0.4 + h2 * 7.0;
float on = step(0.4, fract(Time * rate + h * 7.0));
float led = 1.0 - smoothstep(0.16, 0.3, length(fp * vec2(1.0, 0.5)));
vec3 col = h < 0.55 ? vec3(0.1, 1.0, 0.3) : (h < 0.82 ? vec3(1.0, 0.55, 0.08) : vec3(0.2, 0.5, 1.0));
float present = step(0.3, fract(h * 13.1)) * step(0.06, UV.y) * step(UV.y, 0.94);
float strobe = step(0.5, fract(Time * 2.2 + h * 0.15));
col = mix(col, vec3(1.0, 0.04, 0.02), Alarm);
on = mix(on, strobe, Alarm * step(0.25, h2));
Color = col * led * on * present;
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
