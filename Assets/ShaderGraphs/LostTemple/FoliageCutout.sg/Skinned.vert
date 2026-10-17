$input a_position, a_normal, a_texcoord0, a_tangent, a_bitangent, i_data0, i_data1, i_data2, i_data3, a_indices, a_weight
$output v_worldPos, v_normal, v_tangent, v_bitangent, v_texcoord0, v_viewPos, v_objectPos, v_objectNormal

// Generated from Assets/ShaderGraphs/LostTemple/FoliageCutout.shadergraph by the shader graph compiler: edit the graph, not this file.
#define SG_ALPHA_CLIP 1
#define SG_OFFSET_WORLD 1
#define SG_SKINNED 1

#include "Common.sh"
#if SG_SKINNED
#include "Skinning.sh"
#endif
#include "ShaderGraph/SGLib.sh"

uniform vec4 u_sgParams[16];
SAMPLER2D(s_sgTex0, 0); // Albedo
// u_sgParams[0]: Tint (Vector 3)
// u_sgParams[1]: Wind Strength (Float)
// u_sgParams[2]: Wind Speed (Float)
// u_sgParams[3]: Sway Height (Float)


void main()
{
	// Instanced: the model matrix comes from the instance buffer (and the bone palette when skinned).
	mat4 sg_model = mtxFromCols(i_data0, i_data1, i_data2, i_data3);
#if SG_SKINNED
	sg_model = mul(sg_model, skinMatrix(a_indices, a_weight));
#endif
	mat3 sg_normalMatrix = cofactor(sg_model);

	vec3 sg_PositionObject = a_position;
	vec3 sg_PositionWorld = mul(sg_model, vec4(a_position, 1.0)).xyz;
	float sg_Time = u_time.y;
	float sg_DeltaTime = u_time.x;

	// Split #8
	vec3 n8_In = sg_PositionWorld;
	// Multiply #10
	float n10_Out = n8_In.x * 0.310000002;
	// Multiply #11
	float n11_Out = n8_In.z * 0.230000004;
	// Add #12
	float n12_Out = n10_Out + n11_Out;
	// Multiply #13
	float n13_Out = sg_Time * u_sgParams[2].x;
	// Add #14
	float n14_Out = n12_Out + n13_Out;
	// Sine #15
	float n15_Out = sin(n14_Out);
	// Multiply #16
	float n16_Out = n14_Out * 2.36999989;
	// Add #17
	float n17_Out = n16_Out + 1.29999995;
	// Sine #18
	float n18_Out = sin(n17_Out);
	// Multiply #19
	float n19_Out = n18_Out * 0.349999994;
	// Add #20
	float n20_Out = n15_Out + n19_Out;
	// Multiply #35
	float n35_Out = sg_Time * 6.5;
	// Multiply #36
	float n36_Out = n8_In.x * 3.0999999;
	// Multiply #37
	float n37_Out = n8_In.y * 4.69999981;
	// Add #38
	float n38_Out = n36_Out + n37_Out;
	// Add #39
	float n39_Out = n35_Out + n38_Out;
	// Sine #40
	float n40_Out = sin(n39_Out);
	// Multiply #41
	float n41_Out = n40_Out * 0.119999997;
	// Add #42
	float n42_Out = n20_Out + n41_Out;
	// Split #30
	vec3 n30_In = sg_PositionObject;
	// Divide #31
	float n31_Out = n30_In.y / u_sgParams[3].x;
	// Saturate #32
	float n32_Out = clamp(n31_Out, 0.0, 1.0);
	// Multiply #33
	float n33_Out = n32_Out * n32_Out;
	// Multiply #21
	float n21_Out = sg_Time * 0.370000005;
	// Multiply #22
	float n22_Out = n8_In.x * 0.0500000007;
	// Add #23
	float n23_Out = n21_Out + n22_Out;
	// Sine #24
	float n24_Out = sin(n23_Out);
	// Multiply #25
	float n25_Out = n24_Out * 0.5;
	// Add #26
	float n26_Out = n25_Out + 0.5;
	// Add #27
	float n27_Out = 0.449999988 + n26_Out;
	// Multiply #28
	float n28_Out = u_sgParams[1].x * n27_Out;
	// Multiply #34
	float n34_Out = n33_Out * n28_Out;
	// Multiply #43
	float n43_Out = n42_Out * n34_Out;
	// Multiply #44
	float n44_Out = n14_Out * 0.829999983;
	// Cosine #45
	float n45_Out = cos(n44_Out);
	// Multiply #46
	float n46_Out = n34_Out * 0.600000024;
	// Multiply #47
	float n47_Out = n45_Out * n46_Out;
	// Combine #48
	vec4 n48_RGBA = vec4(n43_Out, 0.0, n47_Out, 1.0);
	// Outputs
	vec3 sgOut_PositionOffset = n48_RGBA.xyz;

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
