$input a_position, a_normal, a_texcoord0, a_tangent, a_bitangent, i_data0, i_data1, i_data2, i_data3, a_indices, a_weight
$output v_worldPos, v_normal, v_tangent, v_bitangent, v_texcoord0, v_viewPos, v_objectPos, v_objectNormal

// Generated from Assets/ShaderGraphs/LaunchNight/RoadmapSlide.shadergraph by the shader graph compiler: edit the graph, not this file.
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

void sgCustom_Slide_8256(vec2 UV, out float Mask1, out float Mask2, out float Mask3)
{
Mask1 = 0.0;
Mask2 = 0.0;
Mask3 = 0.0;
{
    vec2 q = vec2((UV.x - 0.07) / 0.074176, (UV.y - 0.08) / 0.09);
    if (q.y >= 0.0 && q.y < 1.0 && q.x >= 0.0 && q.x < 10.0)
    {
        float ci = floor(q.x);
        float px = floor(fract(q.x) * 6.0);
        float py = floor(q.y * 7.0);
        float glo = 0.0;
        float ghi = 0.0;
        if (ci > -0.5 && ci < 0.5) { glo = 575022.0; ghi = 22837.0; }
        if (ci > 0.5 && ci < 1.5) { glo = 305544.0; ghi = 8479.0; }
        if (ci > 2.5 && ci < 3.5) { glo = 509487.0; ghi = 17701.0; }
        if (ci > 3.5 && ci < 4.5) { glo = 575022.0; ghi = 14897.0; }
        if (ci > 4.5 && ci < 5.5) { glo = 1033774.0; ghi = 17969.0; }
        if (ci > 5.5 && ci < 6.5) { glo = 575023.0; ghi = 15921.0; }
        if (ci > 6.5 && ci < 7.5) { glo = 710513.0; ghi = 17969.0; }
        if (ci > 7.5 && ci < 8.5) { glo = 1033774.0; ghi = 17969.0; }
        if (ci > 8.5 && ci < 9.5) { glo = 509487.0; ghi = 1057.0; }
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
{
    vec2 q = vec2((UV.x - 0.07) / 0.037088, (UV.y - 0.3) / 0.045);
    if (q.y >= 0.0 && q.y < 1.0 && q.x >= 0.0 && q.x < 16.0)
    {
        float ci = floor(q.x);
        float px = floor(fract(q.x) * 6.0);
        float py = floor(q.y * 7.0);
        float glo = 0.0;
        float ghi = 0.0;
        if (ci > -0.5 && ci < 0.5) { glo = 135364.0; ghi = 14468.0; }
        if (ci > 0.5 && ci < 1.5) { glo = 0.0; ghi = 6336.0; }
        if (ci > 2.5 && ci < 3.5) { glo = 459838.0; ghi = 15888.0; }
        if (ci > 3.5 && ci < 4.5) { glo = 1033777.0; ghi = 17969.0; }
        if (ci > 4.5 && ci < 5.5) { glo = 135310.0; ghi = 14468.0; }
        if (ci > 5.5 && ci < 6.5) { glo = 509487.0; ghi = 1057.0; }
        if (ci > 7.5 && ci < 8.5) { glo = 710513.0; ghi = 17969.0; }
        if (ci > 8.5 && ci < 9.5) { glo = 575022.0; ghi = 14897.0; }
        if (ci > 9.5 && ci < 10.5) { glo = 575022.0; ghi = 14897.0; }
        if (ci > 10.5 && ci < 11.5) { glo = 708145.0; ghi = 17977.0; }
        if (ci > 11.5 && ci < 12.5) { glo = 459838.0; ghi = 15888.0; }
        if (ci > 12.5 && ci < 13.5) { glo = 1033777.0; ghi = 17969.0; }
        if (ci > 13.5 && ci < 14.5) { glo = 575022.0; ghi = 14897.0; }
        if (ci > 14.5 && ci < 15.5) { glo = 135327.0; ghi = 4228.0; }
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
{
    vec2 q = vec2((UV.x - 0.07) / 0.037088, (UV.y - 0.4) / 0.045);
    if (q.y >= 0.0 && q.y < 1.0 && q.x >= 0.0 && q.x < 6.0)
    {
        float ci = floor(q.x);
        float px = floor(fract(q.x) * 6.0);
        float py = floor(q.y * 7.0);
        float glo = 0.0;
        float ghi = 0.0;
        if (ci > -0.5 && ci < 0.5) { glo = 279086.0; ghi = 31812.0; }
        if (ci > 0.5 && ci < 1.5) { glo = 0.0; ghi = 6336.0; }
        if (ci > 2.5 && ci < 3.5) { glo = 279086.0; ghi = 4100.0; }
        if (ci > 3.5 && ci < 4.5) { glo = 279086.0; ghi = 4100.0; }
        if (ci > 4.5 && ci < 5.5) { glo = 279086.0; ghi = 4100.0; }
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
{
    vec2 q = vec2((UV.x - 0.07) / 0.037088, (UV.y - 0.5) / 0.045);
    if (q.y >= 0.0 && q.y < 1.0 && q.x >= 0.0 && q.x < 9.0)
    {
        float ci = floor(q.x);
        float px = floor(fract(q.x) * 6.0);
        float py = floor(q.y * 7.0);
        float glo = 0.0;
        float ghi = 0.0;
        if (ci > -0.5 && ci < 0.5) { glo = 266527.0; ghi = 14896.0; }
        if (ci > 0.5 && ci < 1.5) { glo = 0.0; ghi = 6336.0; }
        if (ci > 2.5 && ci < 3.5) { glo = 509487.0; ghi = 1057.0; }
        if (ci > 3.5 && ci < 4.5) { glo = 509487.0; ghi = 17701.0; }
        if (ci > 4.5 && ci < 5.5) { glo = 575022.0; ghi = 14897.0; }
        if (ci > 5.5 && ci < 6.5) { glo = 492607.0; ghi = 1057.0; }
        if (ci > 6.5 && ci < 7.5) { glo = 135310.0; ghi = 14468.0; }
        if (ci > 7.5 && ci < 8.5) { glo = 135327.0; ghi = 4228.0; }
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
{
    vec2 q = vec2((UV.x - 0.07) / 0.037088, (UV.y - 0.6) / 0.045);
    if (q.y >= 0.0 && q.y < 1.0 && q.x >= 0.0 && q.x < 8.0)
    {
        float ci = floor(q.x);
        float px = floor(fract(q.x) * 6.0);
        float py = floor(q.y * 7.0);
        float glo = 0.0;
        float ghi = 0.0;
        if (ci > -0.5 && ci < 0.5) { glo = 305544.0; ghi = 8479.0; }
        if (ci > 0.5 && ci < 1.5) { glo = 0.0; ghi = 6336.0; }
        if (ci > 2.5 && ci < 3.5) { glo = 459838.0; ghi = 15888.0; }
        if (ci > 3.5 && ci < 4.5) { glo = 33825.0; ghi = 31777.0; }
        if (ci > 4.5 && ci < 5.5) { glo = 492607.0; ghi = 31777.0; }
        if (ci > 5.5 && ci < 6.5) { glo = 492607.0; ghi = 31777.0; }
        if (ci > 6.5 && ci < 7.5) { glo = 509487.0; ghi = 1057.0; }
        float hit = 0.0;
        if (px < 5.0)

        {
            float b = py * 5.0 + px;
            float word = b < 20.0 ? glo : ghi;
            float shift = b < 20.0 ? b : b - 20.0;
            hit = mod(floor(word / exp2(shift)), 2.0);
        }
        
        Mask3 = max(Mask3, hit);
    }
}
{
    vec2 q = vec2((UV.x - 0.53) / 0.024725, (UV.y - 0.5) / 0.03);
    if (q.y >= 0.0 && q.y < 1.0 && q.x >= 0.0 && q.x < 11.0)
    {
        float ci = floor(q.x);
        float px = floor(fract(q.x) * 6.0);
        float py = floor(q.y * 7.0);
        float glo = 0.0;
        float ghi = 0.0;
        if (ci > -0.5 && ci < 0.5) { glo = 706097.0; ghi = 10933.0; }
        if (ci > 0.5 && ci < 1.5) { glo = 492607.0; ghi = 31777.0; }
        if (ci > 2.5 && ci < 3.5) { glo = 1033774.0; ghi = 17969.0; }
        if (ci > 3.5 && ci < 4.5) { glo = 509487.0; ghi = 17701.0; }
        if (ci > 4.5 && ci < 5.5) { glo = 492607.0; ghi = 31777.0; }
        if (ci > 6.5 && ci < 7.5) { glo = 1033777.0; ghi = 17969.0; }
        if (ci > 7.5 && ci < 8.5) { glo = 492607.0; ghi = 31777.0; }
        if (ci > 8.5 && ci < 9.5) { glo = 509487.0; ghi = 17701.0; }
        if (ci > 9.5 && ci < 10.5) { glo = 492607.0; ghi = 31777.0; }
        float hit = 0.0;
        if (px < 5.0)

        {
            float b = py * 5.0 + px;
            float word = b < 20.0 ? glo : ghi;
            float shift = b < 20.0 ? b : b - 20.0;
            hit = mod(floor(word / exp2(shift)), 2.0);
        }
        
        Mask2 = max(Mask2, hit);
    }
}
{
    vec2 q = vec2((UV.x - 0.07) / 0.020604, (UV.y - 0.93) / 0.025);
    if (q.y >= 0.0 && q.y < 1.0 && q.x >= 0.0 && q.x < 31.0)
    {
        float ci = floor(q.x);
        float px = floor(fract(q.x) * 6.0);
        float py = floor(q.y * 7.0);
        float glo = 0.0;
        float ghi = 0.0;
        if (ci > -0.5 && ci < 0.5) { glo = 34350.0; ghi = 14881.0; }
        if (ci > 0.5 && ci < 1.5) { glo = 575022.0; ghi = 14897.0; }
        if (ci > 1.5 && ci < 2.5) { glo = 708145.0; ghi = 17977.0; }
        if (ci > 2.5 && ci < 3.5) { glo = 492607.0; ghi = 1057.0; }
        if (ci > 3.5 && ci < 4.5) { glo = 135310.0; ghi = 14468.0; }
        if (ci > 4.5 && ci < 5.5) { glo = 575023.0; ghi = 15921.0; }
        if (ci > 5.5 && ci < 6.5) { glo = 492607.0; ghi = 31777.0; }
        if (ci > 6.5 && ci < 7.5) { glo = 708145.0; ghi = 17977.0; }
        if (ci > 7.5 && ci < 8.5) { glo = 135327.0; ghi = 4228.0; }
        if (ci > 8.5 && ci < 9.5) { glo = 135310.0; ghi = 14468.0; }
        if (ci > 9.5 && ci < 10.5) { glo = 1033774.0; ghi = 17969.0; }
        if (ci > 10.5 && ci < 11.5) { glo = 33825.0; ghi = 31777.0; }
        if (ci > 12.5 && ci < 13.5) { glo = 1015808.0; ghi = 0.0; }
        if (ci > 14.5 && ci < 15.5) { glo = 575023.0; ghi = 15921.0; }
        if (ci > 15.5 && ci < 16.5) { glo = 575022.0; ghi = 14897.0; }
        if (ci > 17.5 && ci < 18.5) { glo = 708145.0; ghi = 17977.0; }
        if (ci > 18.5 && ci < 19.5) { glo = 575022.0; ghi = 14897.0; }
        if (ci > 19.5 && ci < 20.5) { glo = 135327.0; ghi = 4228.0; }
        if (ci > 21.5 && ci < 22.5) { glo = 459838.0; ghi = 15888.0; }
        if (ci > 22.5 && ci < 23.5) { glo = 1033777.0; ghi = 17969.0; }
        if (ci > 23.5 && ci < 24.5) { glo = 575022.0; ghi = 14897.0; }
        if (ci > 24.5 && ci < 25.5) { glo = 706097.0; ghi = 10933.0; }
        if (ci > 26.5 && ci < 27.5) { glo = 135327.0; ghi = 4228.0; }
        if (ci > 27.5 && ci < 28.5) { glo = 492607.0; ghi = 31777.0; }
        if (ci > 28.5 && ci < 29.5) { glo = 1033774.0; ghi = 17969.0; }
        if (ci > 29.5 && ci < 30.5) { glo = 710513.0; ghi = 17969.0; }
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

void sgCustom_Chart_75953(vec2 UV, out float Axes, out float Curve, out float Here)
{
vec2 p = (UV - vec2(0.52, 0.86)) / vec2(0.42, -0.5);
float axis = (step(abs(p.x), 0.006) + step(abs(p.y), 0.012)) * step(-0.02, p.x) * step(p.x, 1.0) * step(-0.02, p.y) * step(p.y, 1.0);
float curve = 0.06 + 0.02 * sin(p.x * 30.0) + pow(max(p.x - 0.55, 0.0) * 2.2, 3.0);
float stroke = 1.0 - smoothstep(0.012, 0.03, abs(p.y - curve));
stroke *= step(0.0, p.x) * step(p.x, 0.98);
float here = 1.0 - smoothstep(0.018, 0.03, length((p - vec2(0.2, 0.08)) * vec2(1.0, 0.8)));
float arrow = step(abs(p.x - 0.2), 0.008) * step(0.12, p.y) * step(p.y, 0.32);
Axes = clamp(axis, 0.0, 1.0);
Curve = stroke;
Here = max(here, arrow);
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
