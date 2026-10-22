$input a_position, a_normal, a_texcoord0, a_tangent, a_bitangent, i_data0, i_data1, i_data2, i_data3, a_indices, a_weight
$output v_worldPos, v_normal, v_tangent, v_bitangent, v_texcoord0, v_viewPos, v_objectPos, v_objectNormal

// Generated from Assets/ShaderGraphs/LaunchNight/CityWindows.shadergraph by the shader graph compiler: edit the graph, not this file.
#define SG_SKINNED 1

#include "Common.sh"
#if SG_SKINNED
#include "Skinning.sh"
#endif
#include "ShaderGraph/SGLib.sh"

uniform vec4 u_sgParams[16];
// u_sgParams[0]: Facade (Vector 3)
// u_sgParams[1]: Intensity (Float)

void sgCustom_City_45628(vec3 P, vec3 N, float Time, out vec3 Emit, out float Window)
{
vec3 an = abs(N);
vec2 uv = an.x > an.z ? P.zy : P.xy;
vec2 gp = uv / vec2(3.1, 3.5);
vec2 id = floor(gp);
vec2 fp = fract(gp);
float win = step(0.16, fp.x) * step(fp.x, 0.84) * step(0.22, fp.y) * step(fp.y, 0.84);
float n = fract(sin(dot(id + floor(P.xz * 0.05) * 13.0, vec2(12.9898, 78.233)) + floor(an.x * 1.5) * 3.1) * 43758.5453);
float lit = step(0.64, n);
float tv = step(0.64, n) * step(n, 0.67) * (0.5 + 0.5 * sin(Time * (3.0 + n * 9.0) + n * 40.0));
vec3 warm = vec3(1.0, 0.72, 0.42);
vec3 cool = vec3(0.6, 0.78, 1.0);
vec3 col = fract(n * 31.7) < 0.7 ? warm : cool;
col = mix(col, vec3(0.3, 0.5, 1.0), step(0.0001, tv));
float side = step(an.y, 0.5);
Emit = col * win * lit * side * (0.4 + 0.6 * fract(n * 17.3)) * (1.0 - 0.6 * tv);
Window = win * side;
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
