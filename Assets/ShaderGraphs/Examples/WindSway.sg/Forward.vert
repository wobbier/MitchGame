$input a_position, a_normal, a_texcoord0, a_tangent, a_bitangent, i_data0, i_data1, i_data2, i_data3
$output v_worldPos, v_normal, v_tangent, v_bitangent, v_texcoord0, v_viewPos, v_objectPos, v_objectNormal

// Generated from Assets/ShaderGraphs/Examples/WindSway.shadergraph by the shader graph compiler: edit the graph, not this file.

#include "Common.sh"
#if SG_SKINNED
#include "Skinning.sh"
#endif
#include "ShaderGraph/SGLib.sh"

uniform vec4 u_sgParams[16];
// u_sgParams[0]: Strength (Float)
// u_sgParams[1]: Speed (Float)


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

	// Multiply #9
	float n9_Out = sg_Time * u_sgParams[1].x;
	// Split #7
	vec3 n7_In = sg_PositionWorld;
	// Add #10
	float n10_Out = n9_Out + n7_In.x;
	// Sine #11
	float n11_Out = sin(n10_Out);
	// Multiply #14
	float n14_Out = n11_Out * u_sgParams[0].x;
	// Split #5
	vec3 n5_In = sg_PositionObject;
	// Saturate #12
	float n12_Out = clamp(n5_In.y, 0.0, 1.0);
	// Square #13
	float n13_Out = n12_Out * n12_Out;
	// Multiply #15
	float n15_Out = n14_Out * n13_Out;
	// Combine #16
	vec4 n16_RGBA = vec4(n15_Out, 0.0, 0.0, 1.0);
	// Outputs
	vec3 sgOut_PositionOffset = n16_RGBA.xyz;

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
