$input a_position, a_normal, a_texcoord0, a_tangent, a_bitangent, i_data0, i_data1, i_data2, i_data3, a_indices, a_weight
$output v_worldPos, v_normal, v_tangent, v_bitangent, v_texcoord0, v_viewPos, v_objectPos, v_objectNormal

// Generated from Assets/ShaderGraphs/LaunchNight/CodeScreen.shadergraph by the shader graph compiler: edit the graph, not this file.
#define SG_SKINNED 1

#include "Common.sh"
#if SG_SKINNED
#include "Skinning.sh"
#endif
#include "ShaderGraph/SGLib.sh"

uniform vec4 u_sgParams[16];
// u_sgParams[0]: Scroll Speed (Float)
// u_sgParams[1]: Seed (Float)
// u_sgParams[2]: Brightness (Float)
// u_sgParams[3]: Background (Vector 3)
// u_sgParams[4]: UV Rect (Vector 4)
// u_sgParams[5]: Flip (Vector 2)

void sgCustom_CodeLines_44436(vec2 UV, float Time, float Speed, float Seed, out vec3 Color)
{
float rows = 26.0;
float yy = UV.y * rows + Time * Speed;
float row = floor(yy);
float fy = fract(yy);
float h = fract(sin(row * 12.9898 + Seed * 78.233) * 43758.5453);
float h2 = fract(sin(row * 39.346 + Seed * 11.135) * 24634.6345);
float cols = 70.0;
float indent = floor(h2 * 4.0) * 2.0;
float gutter = UV.x * cols;
float cx = gutter - 4.0 - indent;
float c = floor(cx);
float fx = fract(cx);
float len = floor(6.0 + h * 44.0);
float hc = fract(sin((c + row * 97.0) * 7.31 + Seed) * 9137.17);
float word = floor((c + floor(h * 7.0)) / 5.0);
float hw = fract(sin((word + row * 31.0) * 3.17 + Seed * 1.7) * 5131.7);
float blank = step(h, 0.1);
float ink = step(0.0, c) * step(c, len) * step(0.15, hc) * (1.0 - blank);
float glyph = step(0.2, fy) * step(fy, 0.76) * step(0.12, fx) * step(fx, 0.88);
vec3 col = vec3(0.82, 0.85, 0.9);
if (hw < 0.2) col = vec3(0.78, 0.45, 0.98);
else if (hw < 0.34) col = vec3(1.0, 0.62, 0.3);
else if (hw < 0.52) col = vec3(0.36, 0.68, 1.0);
if (h2 > 0.86) col = vec3(0.4, 0.75, 0.38);
float numbers = step(gutter, 2.6) * step(0.4, fract(sin(row * 3.3) * 91.7)) * glyph;
float cursor = step(abs(UV.y - 0.93), 0.016) * step(abs(UV.x - (0.06 + fract(Time * 0.37 + Seed) * 0.5)), 0.008) * step(0.5, fract(Time * 1.6));
Color = col * ink * glyph + vec3(0.25, 0.27, 0.32) * numbers + vec3(0.9, 0.9, 0.9) * cursor;
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
