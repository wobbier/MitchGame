$input a_position, a_normal, a_texcoord0, a_tangent, a_bitangent, i_data0, i_data1, i_data2, i_data3
$output v_worldPos, v_normal, v_tangent, v_bitangent, v_texcoord0, v_viewPos, v_objectPos, v_objectNormal

// Generated from Assets/ShaderGraphs/Examples/TwistGlitch.shadergraph by the shader graph compiler: edit the graph, not this file.
#define SG_NORMAL_WORLD 1

#include "Common.sh"
#if SG_SKINNED
#include "Skinning.sh"
#endif
#include "ShaderGraph/SGLib.sh"

uniform vec4 u_sgParams[16];
// u_sgParams[0]: Twist (Float)
// u_sgParams[1]: Twist Speed (Float)
// u_sgParams[2]: Bands (Float)
// u_sgParams[3]: Glitch Rate (Float)
// u_sgParams[4]: Glitch Amount (Float)
// u_sgParams[5]: Glitch Distance (Float)
// u_sgParams[6]: Burst Rate (Float)
// u_sgParams[7]: Glitch Color A (Vector 3)
// u_sgParams[8]: Glitch Color B (Vector 3)


void main()
{
	// Instanced: the model matrix comes from the instance buffer (and the bone palette when skinned).
	mat4 sg_model = mtxFromCols(i_data0, i_data1, i_data2, i_data3);
#if SG_SKINNED
	sg_model = mul(sg_model, skinMatrix(a_indices, a_weight));
#endif
	mat3 sg_normalMatrix = cofactor(sg_model);

	vec3 sg_PositionObject = a_position;
	float sg_Time = u_time.y;
	float sg_DeltaTime = u_time.x;

	// Split #12
	vec3 n12_In = sg_PositionObject;
	// Multiply #16
	float n16_Out = n12_In.y * u_sgParams[0].x;
	// Multiply #14
	float n14_Out = sg_Time * u_sgParams[1].x;
	// Sine #15
	float n15_Out = sin(n14_Out);
	// Multiply #17
	float n17_Out = n16_Out * n15_Out;
	// Rotate About Axis #18
	vec3 n18_Out = sgRotateAboutAxis(sg_PositionObject, vec3(0.0, 1.0, 0.0), n17_Out);
	// Subtract #40
	vec3 n40_Out = n18_Out - sg_PositionObject;
	// Multiply #19
	float n19_Out = n12_In.y * u_sgParams[2].x;
	// Floor #20
	float n20_Out = floor(n19_Out);
	// Add #25
	float n25_Out = n20_Out + 17.0;
	// Multiply #21
	float n21_Out = sg_Time * u_sgParams[3].x;
	// Floor #22
	float n22_Out = floor(n21_Out);
	// Combine #26
	vec4 n26_RGBA = vec4(n25_Out, n22_Out, 0.0, 1.0);
	// Value Noise #27
	float n27_Out = sgValueNoise(n26_RGBA.xy, 1.0);
	// Multiply #36
	float n36_Out = n27_Out * 2.0;
	// Subtract #37
	float n37_Out = n36_Out - 1.0;
	// Multiply #38
	float n38_Out = n37_Out * u_sgParams[5].x;
	// One Minus #33
	float n33_Out = 1.0 - u_sgParams[4].x;
	// Combine #23
	vec4 n23_RGBA = vec4(n20_Out, n22_Out, 0.0, 1.0);
	// Value Noise #24
	float n24_Out = sgValueNoise(n23_RGBA.xy, 1.0);
	// Step #34
	float n34_Out = step(n33_Out, n24_Out);
	// Multiply #28
	float n28_Out = sg_Time * u_sgParams[6].x;
	// Floor #29
	float n29_Out = floor(n28_Out);
	// Combine #30
	vec4 n30_RGBA = vec4(n29_Out, 5.0, 0.0, 1.0);
	// Value Noise #31
	float n31_Out = sgValueNoise(n30_RGBA.xy, 1.0);
	// Step #32
	float n32_Out = step(0.449999988, n31_Out);
	// Multiply #35
	float n35_Out = n34_Out * n32_Out;
	// Multiply #39
	float n39_Out = n38_Out * n35_Out;
	// Combine #41
	vec4 n41_RGBA = vec4(n39_Out, 0.0, 0.0, 1.0);
	// Add #42
	vec3 n42_Out = n40_Out + n41_RGBA.xyz;
	// Outputs
	vec3 sgOut_PositionOffset = n42_Out;

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
