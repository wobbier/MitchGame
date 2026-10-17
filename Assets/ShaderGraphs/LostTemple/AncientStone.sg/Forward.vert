$input a_position, a_normal, a_texcoord0, a_tangent, a_bitangent, i_data0, i_data1, i_data2, i_data3
$output v_worldPos, v_normal, v_tangent, v_bitangent, v_texcoord0, v_viewPos, v_objectPos, v_objectNormal

// Generated from Assets/ShaderGraphs/LostTemple/AncientStone.shadergraph by the shader graph compiler: edit the graph, not this file.

#include "Common.sh"
#if SG_SKINNED
#include "Skinning.sh"
#endif
#include "ShaderGraph/SGLib.sh"

uniform vec4 u_sgParams[16];
SAMPLER2D(s_sgTex0, 0); // Stone Texture
SAMPLER2D(s_sgTex1, 1); // Moss Texture
// u_sgParams[0]: Stone Tint (Vector 3)
// u_sgParams[1]: Moss Color (Vector 3)
// u_sgParams[2]: Moss Amount (Float)
// u_sgParams[3]: Tile (Float)
// u_sgParams[4]: Wet Height (Float)
// u_sgParams[5]: Roughness (Float)
// u_sgParams[6]: Masonry (Float)
// u_sgParams[7]: Block Size (Vector 2)
// u_sgParams[8]: Frame Yaw (Float)
// u_sgParams[9]: Block Variation (Float)

void sgCustom_Masonry_17942(vec3 Position, vec3 Normal, vec2 BlockSize, float Gap, float FrameYaw, out float Mortar, out float Bevel, out float Block)
{
float a = radians(FrameYaw);
float c = cos(a);
float s = sin(a);
vec3 p = vec3(Position.x * c - Position.z * s, Position.y, Position.x * s + Position.z * c);
vec3 n = abs(vec3(Normal.x * c - Normal.z * s, Normal.y, Normal.x * s + Normal.z * c));
vec2 uv = n.y > 0.7 ? p.xz : (n.x > n.z ? p.zy : p.xy);
vec2 size = n.y > 0.7 ? vec2_splat(BlockSize.x * 0.8) : BlockSize;
vec2 q = uv / size;
q.x += mod(floor(q.y), 2.0) * 0.5;
vec2 cell = floor(q);
vec2 f = fract(q);
vec2 edge = min(f, vec2_splat(1.0) - f) * size;
float d = min(edge.x, edge.y);
Mortar = 1.0 - smoothstep(Gap * 0.5, Gap * 0.5 + 0.012, d);
Bevel = smoothstep(Gap * 0.5, Gap * 0.5 + 0.07, d);
Block = fract(sin(dot(cell, vec2(12.9898, 78.233))) * 43758.5453);
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
