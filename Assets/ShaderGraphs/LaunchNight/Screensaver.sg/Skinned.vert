$input a_position, a_normal, a_texcoord0, a_tangent, a_bitangent, i_data0, i_data1, i_data2, i_data3, a_indices, a_weight
$output v_worldPos, v_normal, v_tangent, v_bitangent, v_texcoord0, v_viewPos, v_objectPos, v_objectNormal

// Generated from Assets/ShaderGraphs/LaunchNight/Screensaver.shadergraph by the shader graph compiler: edit the graph, not this file.
#define SG_SKINNED 1

#include "Common.sh"
#if SG_SKINNED
#include "Skinning.sh"
#endif
#include "ShaderGraph/SGLib.sh"

uniform vec4 u_sgParams[16];
// u_sgParams[0]: Brightness (Float)
// u_sgParams[1]: UV Rect (Vector 4)
// u_sgParams[2]: Flip (Vector 2)

void sgCustom_Bounce_42153(vec2 UV, float Time, out vec2 Local, out vec3 Tint)
{
float w = 0.33;
float hgt = 0.16;
float tx = Time * 0.083;
float ty = Time * 0.061;
vec2 o = vec2(abs(fract(tx) * 2.0 - 1.0) * (1.0 - w), abs(fract(ty) * 2.0 - 1.0) * (1.0 - hgt));
Local = UV - o;
float bounces = floor(tx * 2.0) + floor(ty * 2.0);
Tint = vec3_splat(0.5) + 0.5 * cos(6.2831853 * (bounces * 0.27 + vec3(0.0, 0.33, 0.67)));
}

void sgCustom_Sleepy_27957(vec2 UV, out float Mask1, out float Mask2, out float Mask3)
{
Mask1 = 0.0;
Mask2 = 0.0;
Mask3 = 0.0;
{
    vec2 q = vec2((UV.x - 0.0) / 0.085714, (UV.y - 0.0) / 0.16);
    if (q.y >= 0.0 && q.y < 1.0 && q.x >= 0.0 && q.x < 6.0)
    {
        float ci = floor(q.x);
        float px = floor(fract(q.x) * 6.0);
        float py = floor(q.y * 7.0);
        float glo = 0.0;
        float ghi = 0.0;
        if (ci > -0.5 && ci < 0.5) { glo = 139807.0; ghi = 31778.0; }
        if (ci > 0.5 && ci < 1.5) { glo = 139807.0; ghi = 31778.0; }
        if (ci > 1.5 && ci < 2.5) { glo = 139807.0; ghi = 31778.0; }
        if (ci > 2.5 && ci < 3.5) { glo = 0.0; ghi = 6336.0; }
        if (ci > 3.5 && ci < 4.5) { glo = 0.0; ghi = 6336.0; }
        if (ci > 4.5 && ci < 5.5) { glo = 0.0; ghi = 6336.0; }
        float hit = 0.0;
        if (px < 5.0)

        {
            float b = py * 5.0 + px;
            float word = b < 20.0 ? glo : ghi;
            float shift = b < 20.0 ? b : b - 20.0;
            hit = mod(floor(word / exp2(shift)), 2.0);
        }
        
        Mask1 = max(Mask1, hit);
    }
}
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
