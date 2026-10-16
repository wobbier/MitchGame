$input a_position, a_normal, a_texcoord0, a_tangent, a_bitangent, i_data0, i_data1, i_data2, i_data3, a_indices, a_weight
$output v_worldPos, v_normal, v_tangent, v_bitangent, v_texcoord0, v_viewPos, v_objectPos, v_objectNormal

// Generated from Assets/ShaderGraphs/Examples/PlasmaBlob.shadergraph by the shader graph compiler: edit the graph, not this file.
#define SG_NORMAL_WORLD 1
#define SG_SKINNED 1

#include "Common.sh"
#if SG_SKINNED
#include "Skinning.sh"
#endif
#include "ShaderGraph/SGLib.sh"

uniform vec4 u_sgParams[16];
// u_sgParams[0]: Amplitude (Float)
// u_sgParams[1]: Noise Scale (Float)
// u_sgParams[2]: Flow Speed (Float)
// u_sgParams[3]: Pulse Speed (Float)
// u_sgParams[4]: Glow Color (Vector 3)
// u_sgParams[5]: Glow (Float)
// u_sgParams[6]: Hue Speed (Float)
// u_sgParams[7]: Crust Color (Vector 3)


void main()
{
	// Instanced: the model matrix comes from the instance buffer (and the bone palette when skinned).
	mat4 sg_model = mtxFromCols(i_data0, i_data1, i_data2, i_data3);
#if SG_SKINNED
	sg_model = mul(sg_model, skinMatrix(a_indices, a_weight));
#endif
	mat3 sg_normalMatrix = cofactor(sg_model);

	vec3 sg_NormalObject = a_normal;
	float sg_Time = u_time.y;
	float sg_DeltaTime = u_time.x;

	// Swizzle .xy #17
	vec2 n17_Out = (vec4(sg_NormalObject, 1.0)).xy;
	// Multiply #12
	float n12_Out = sg_Time * u_sgParams[2].x;
	// Multiply #13
	float n13_Out = n12_Out * 0.600000024;
	// Combine #14
	vec4 n14_RGBA = vec4(n12_Out, n13_Out, 0.0, 1.0);
	// Add #18
	vec2 n18_Out = n17_Out + n14_RGBA.xy;
	// Fractal Noise #19
	float n19_Out = sgFractalNoise(n18_Out, u_sgParams[1].x, 4.0, 2.0, 0.5);
	// Swizzle .yz #20
	vec2 n20_Out = (vec4(sg_NormalObject, 1.0)).yz;
	// Multiply #15
	float n15_Out = n12_Out * (-0.5);
	// Combine #16
	vec4 n16_RGBA = vec4(n15_Out, n12_Out, 0.0, 1.0);
	// Add #21
	vec2 n21_Out = n20_Out + n16_RGBA.xy;
	// Fractal Noise #22
	float n22_Out = sgFractalNoise(n21_Out, u_sgParams[1].x, 4.0, 2.0, 0.5);
	// Add #23
	float n23_Out = n19_Out + n22_Out;
	// Multiply #24
	float n24_Out = n23_Out * 0.5;
	// Smoothstep #25
	float n25_Out = smoothstep(0.300000012, 0.550000012, n24_Out);
	// Multiply #29
	float n29_Out = n25_Out * u_sgParams[0].x;
	// Multiply #26
	float n26_Out = sg_Time * u_sgParams[3].x;
	// Sine #27
	float n27_Out = sin(n26_Out);
	// Remap #28
	float n28_Out = 0.550000012 + (n27_Out - (-1.0)) * (1.14999998 - 0.550000012) / (1.0 - (-1.0));
	// Multiply #30
	float n30_Out = n29_Out * n28_Out;
	// Multiply #31
	vec3 n31_Out = sg_NormalObject * vec3_splat(n30_Out);
	// Outputs
	vec3 sgOut_PositionOffset = n31_Out;

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
