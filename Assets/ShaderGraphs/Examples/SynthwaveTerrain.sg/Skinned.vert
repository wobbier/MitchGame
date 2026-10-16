$input a_position, a_normal, a_texcoord0, a_tangent, a_bitangent, i_data0, i_data1, i_data2, i_data3, a_indices, a_weight
$output v_worldPos, v_normal, v_tangent, v_bitangent, v_texcoord0, v_viewPos, v_objectPos, v_objectNormal

// Generated from Assets/ShaderGraphs/Examples/SynthwaveTerrain.shadergraph by the shader graph compiler: edit the graph, not this file.
#define SG_OFFSET_WORLD 1
#define SG_FOG 1
#define SG_SKINNED 1

#include "Common.sh"
#if SG_SKINNED
#include "Skinning.sh"
#endif
#include "ShaderGraph/SGLib.sh"

uniform vec4 u_sgParams[16];
// u_sgParams[0]: Height (Float)
// u_sgParams[1]: Valley Width (Float)
// u_sgParams[2]: Noise Scale (Float)
// u_sgParams[3]: Speed (Float)
// u_sgParams[4]: Curvature (Float)
// u_sgParams[5]: Cell Size (Float)
// u_sgParams[6]: Line Width (Float)
// u_sgParams[7]: Low Color (Vector 3)
// u_sgParams[8]: High Color (Vector 3)
// u_sgParams[9]: Fill Color (Vector 3)


void main()
{
	// Instanced: the model matrix comes from the instance buffer (and the bone palette when skinned).
	mat4 sg_model = mtxFromCols(i_data0, i_data1, i_data2, i_data3);
#if SG_SKINNED
	sg_model = mul(sg_model, skinMatrix(a_indices, a_weight));
#endif
	mat3 sg_normalMatrix = cofactor(sg_model);

	vec3 sg_PositionWorld = mul(sg_model, vec4(a_position, 1.0)).xyz;
	vec3 sg_CameraPosition = mul(u_invView, vec4(0.0, 0.0, 0.0, 1.0)).xyz;
	float sg_Time = u_time.y;
	float sg_DeltaTime = u_time.x;

	// Swizzle .xz #13
	vec2 n13_Out = (vec4(sg_PositionWorld, 1.0)).xz;
	// Multiply #15
	float n15_Out = sg_Time * u_sgParams[3].x;
	// Combine #16
	vec4 n16_RGBA = vec4(0.0, n15_Out, 0.0, 1.0);
	// Add #17
	vec2 n17_Out = n13_Out + n16_RGBA.xy;
	// Fractal Noise #18
	float n18_Out = sgFractalNoise(n17_Out, u_sgParams[2].x, 5.0, 2.0, 0.5);
	// Smoothstep #19
	float n19_Out = smoothstep(0.300000012, 0.850000024, n18_Out);
	// Add #21
	float n21_Out = u_sgParams[1].x + 10.0;
	// Split #20
	vec3 n20_In = sg_PositionWorld;
	// Absolute #22
	float n22_Out = abs(n20_In.x);
	// Smoothstep #23
	float n23_Out = smoothstep(u_sgParams[1].x, n21_Out, n22_Out);
	// Multiply #24
	float n24_Out = n19_Out * n23_Out;
	// Multiply #25
	float n25_Out = n24_Out * u_sgParams[0].x;
	// Swizzle .xz #27
	vec2 n27_Out = (vec4(sg_CameraPosition, 1.0)).xz;
	// Distance #28
	float n28_Out = distance(n13_Out, n27_Out);
	// Square #29
	float n29_Out = n28_Out * n28_Out;
	// Multiply #30
	float n30_Out = n29_Out * u_sgParams[4].x;
	// Subtract #31
	float n31_Out = n25_Out - n30_Out;
	// Combine #32
	vec4 n32_RGBA = vec4(0.0, n31_Out, 0.0, 1.0);
	// Outputs
	vec3 sgOut_PositionOffset = n32_RGBA.xyz;

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
