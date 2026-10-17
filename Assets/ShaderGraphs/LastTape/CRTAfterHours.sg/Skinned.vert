$input a_position, a_normal, a_texcoord0, a_tangent, a_bitangent, i_data0, i_data1, i_data2, i_data3, a_indices, a_weight
$output v_worldPos, v_normal, v_tangent, v_bitangent, v_texcoord0, v_viewPos, v_objectPos, v_objectNormal

// Generated from Assets/ShaderGraphs/LastTape/CRTAfterHours.shadergraph by the shader graph compiler: edit the graph, not this file.
#define SG_FOG 1
#define SG_SKINNED 1

#include "Common.sh"
#if SG_SKINNED
#include "Skinning.sh"
#endif
#include "ShaderGraph/SGLib.sh"

uniform vec4 u_sgParams[16];
// u_sgParams[0]: Phosphor (Vector 3)
// u_sgParams[1]: Brightness (Float)

void sgCustom_NoSignal_81184(vec2 UV, float Clock, vec3 Tint, float Gain, out vec3 Color)
{
vec2 p = UV - vec2_splat(0.5);
float border = 1.0-smoothstep(0.44,0.5,max(abs(p.x),abs(p.y)));
float lines = .78 + .22*sin(UV.y*190.0*3.14159265);
float roll = 1.0-smoothstep(0.0,0.075,abs(UV.y-fract(Clock*.12)));
float n = fract(sin(dot(floor(UV*vec2(240.0,180.0)),vec2(12.9898,78.233))+floor(Clock*24.0))*43758.5453);
// Abstract terminal windows and cursor, with no extra screen texture.
float window = step(abs(UV.x-.5),.36)*step(abs(UV.y-.42),.28);
float textRows = step(.77,fract(UV.y*22.0))*step(UV.x,.7)*step(.2,UV.x)*step(.19,UV.y)*step(UV.y,.59);
float cursor = step(abs(UV.x-.3),.035)*step(abs(UV.y-.64),.008)*step(.3,fract(Clock));
vec3 display = Tint*(.10 + window*.13 + textRows*.30 + cursor*.7 + roll*.1 + n*.035);
Color = display*lines*border*Gain;
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
