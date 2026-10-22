$input a_position, a_normal, a_texcoord0, a_tangent, a_bitangent, i_data0, i_data1, i_data2, i_data3, a_indices, a_weight
$output v_worldPos, v_normal, v_tangent, v_bitangent, v_texcoord0, v_viewPos, v_objectPos, v_objectNormal

// Generated from Assets/ShaderGraphs/LaunchNight/CCTVServerRoom.shadergraph by the shader graph compiler: edit the graph, not this file.
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

void sgCustom_Feed_99340(vec2 UV, float Time, vec2 Hot, float FireAmount, out float Gray, out float Fire, out float Backing)
{
float t = Time;
float roll = fract(UV.y * 0.9 - t * 0.17);
float band = smoothstep(0.0, 0.05, roll) * (1.0 - smoothstep(0.05, 0.12, roll));
float n = fract(sin(dot(floor(UV * vec2(320.0, 240.0)) + floor(t * 24.0) * 1.37, vec2(12.9898, 78.233))) * 43758.5453);
float shade = 0.025 + 0.11 * smoothstep(1.0, 0.25, UV.y) + 0.04 * step(0.62, UV.y);
vec2 c = (UV - Hot) * vec2(1.6, 1.0);
float flicker = 0.75 + 0.25 * sin(t * 13.0) * sin(t * 7.3);
float flame = (exp(-dot(c, c) * 22.0) * 1.6 + exp(-dot(c, c) * 4.0) * 0.35) * flicker;
float rack = step(0.5, fract(UV.x * 9.0)) * step(0.3, UV.y) * step(UV.y, 0.8);
float leds = rack * step(0.82, fract(sin(dot(floor(UV * vec2(36.0, 40.0)), vec2(7.13, 3.71))) * 917.13)) * 0.22;
Gray = shade * (1.0 - rack * 0.6) + leds + n * 0.05 + band * 0.07;
Fire = flame * FireAmount;
Backing = FireAmount * step(0.19, UV.x) * step(UV.x, 0.81) * step(0.69, UV.y) * step(UV.y, 0.84);
}

void sgCustom_Overlay_91702(vec2 UV, float Time, out float Mask1, out float Mask2, out float Mask3)
{
Mask1 = 0.0;
Mask2 = 0.0;
Mask3 = 0.0;
{
    vec2 q = vec2((UV.x - 0.05) / 0.038668, (UV.y - 0.06) / 0.06);
    if (q.y >= 0.0 && q.y < 1.0 && q.x >= 0.0 && q.x < 16.0)
    {
        float ci = floor(q.x);
        float px = floor(fract(q.x) * 6.0);
        float py = floor(q.y * 7.0);
        float glo = 0.0;
        float ghi = 0.0;
        if (ci > -0.5 && ci < 0.5) { glo = 34350.0; ghi = 14881.0; }
        if (ci > 0.5 && ci < 1.5) { glo = 1033774.0; ghi = 17969.0; }
        if (ci > 1.5 && ci < 2.5) { glo = 710513.0; ghi = 17969.0; }
        if (ci > 3.5 && ci < 4.5) { glo = 714286.0; ghi = 14899.0; }
        if (ci > 4.5 && ci < 5.5) { glo = 305544.0; ghi = 8479.0; }
        if (ci > 6.5 && ci < 7.5) { glo = 459838.0; ghi = 15888.0; }
        if (ci > 7.5 && ci < 8.5) { glo = 492607.0; ghi = 31777.0; }
        if (ci > 8.5 && ci < 9.5) { glo = 509487.0; ghi = 17701.0; }
        if (ci > 9.5 && ci < 10.5) { glo = 575025.0; ghi = 4433.0; }
        if (ci > 10.5 && ci < 11.5) { glo = 492607.0; ghi = 31777.0; }
        if (ci > 11.5 && ci < 12.5) { glo = 509487.0; ghi = 17701.0; }
        if (ci > 13.5 && ci < 14.5) { glo = 509487.0; ghi = 17701.0; }
        if (ci > 14.5 && ci < 15.5) { glo = 710513.0; ghi = 17969.0; }
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
    vec2 q = vec2((UV.x - 0.62) / 0.038668, (UV.y - 0.06) / 0.06);
    if (q.y >= 0.0 && q.y < 1.0 && q.x >= 0.0 && q.x < 8.0)
    {
        float ci = floor(q.x);
        float px = floor(fract(q.x) * 6.0);
        float py = floor(q.y * 7.0);
        float glo = 0.0;
        float ghi = 0.0;
        if (ci > 1.5 && ci < 2.5) { glo = 6336.0; ghi = 198.0; }
        if (ci > 4.5 && ci < 5.5) { glo = 6336.0; ghi = 198.0; }
        if (ci > -0.5 && ci < 0.5)
        {
            float dv = clamp(floor(mod((13632.0 + Time) / 36000.0, 10.0)), 0.0, 9.0);
            if (dv > -0.5 && dv < 0.5) { glo = 714286.0; ghi = 14899.0; }
            if (dv > 0.5 && dv < 1.5) { glo = 135364.0; ghi = 14468.0; }
            if (dv > 1.5 && dv < 2.5) { glo = 279086.0; ghi = 31812.0; }
            if (dv > 2.5 && dv < 3.5) { glo = 266527.0; ghi = 14896.0; }
            if (dv > 3.5 && dv < 4.5) { glo = 305544.0; ghi = 8479.0; }
            if (dv > 4.5 && dv < 5.5) { glo = 539711.0; ghi = 14896.0; }
            if (dv > 5.5 && dv < 6.5) { glo = 492620.0; ghi = 14897.0; }
            if (dv > 6.5 && dv < 7.5) { glo = 139807.0; ghi = 2114.0; }
            if (dv > 7.5 && dv < 8.5) { glo = 476718.0; ghi = 14897.0; }
            if (dv > 8.5 && dv < 9.5) { glo = 1001006.0; ghi = 6416.0; }
        }
        if (ci > 0.5 && ci < 1.5)
        {
            float dv = clamp(floor(mod((13632.0 + Time) / 3600.0, 10.0)), 0.0, 9.0);
            if (dv > -0.5 && dv < 0.5) { glo = 714286.0; ghi = 14899.0; }
            if (dv > 0.5 && dv < 1.5) { glo = 135364.0; ghi = 14468.0; }
            if (dv > 1.5 && dv < 2.5) { glo = 279086.0; ghi = 31812.0; }
            if (dv > 2.5 && dv < 3.5) { glo = 266527.0; ghi = 14896.0; }
            if (dv > 3.5 && dv < 4.5) { glo = 305544.0; ghi = 8479.0; }
            if (dv > 4.5 && dv < 5.5) { glo = 539711.0; ghi = 14896.0; }
            if (dv > 5.5 && dv < 6.5) { glo = 492620.0; ghi = 14897.0; }
            if (dv > 6.5 && dv < 7.5) { glo = 139807.0; ghi = 2114.0; }
            if (dv > 7.5 && dv < 8.5) { glo = 476718.0; ghi = 14897.0; }
            if (dv > 8.5 && dv < 9.5) { glo = 1001006.0; ghi = 6416.0; }
        }
        if (ci > 2.5 && ci < 3.5)
        {
            float dv = clamp(floor(mod((13632.0 + Time), 3600.0) / 600.0), 0.0, 9.0);
            if (dv > -0.5 && dv < 0.5) { glo = 714286.0; ghi = 14899.0; }
            if (dv > 0.5 && dv < 1.5) { glo = 135364.0; ghi = 14468.0; }
            if (dv > 1.5 && dv < 2.5) { glo = 279086.0; ghi = 31812.0; }
            if (dv > 2.5 && dv < 3.5) { glo = 266527.0; ghi = 14896.0; }
            if (dv > 3.5 && dv < 4.5) { glo = 305544.0; ghi = 8479.0; }
            if (dv > 4.5 && dv < 5.5) { glo = 539711.0; ghi = 14896.0; }
            if (dv > 5.5 && dv < 6.5) { glo = 492620.0; ghi = 14897.0; }
            if (dv > 6.5 && dv < 7.5) { glo = 139807.0; ghi = 2114.0; }
            if (dv > 7.5 && dv < 8.5) { glo = 476718.0; ghi = 14897.0; }
            if (dv > 8.5 && dv < 9.5) { glo = 1001006.0; ghi = 6416.0; }
        }
        if (ci > 3.5 && ci < 4.5)
        {
            float dv = clamp(floor(mod(mod((13632.0 + Time), 3600.0) / 60.0, 10.0)), 0.0, 9.0);
            if (dv > -0.5 && dv < 0.5) { glo = 714286.0; ghi = 14899.0; }
            if (dv > 0.5 && dv < 1.5) { glo = 135364.0; ghi = 14468.0; }
            if (dv > 1.5 && dv < 2.5) { glo = 279086.0; ghi = 31812.0; }
            if (dv > 2.5 && dv < 3.5) { glo = 266527.0; ghi = 14896.0; }
            if (dv > 3.5 && dv < 4.5) { glo = 305544.0; ghi = 8479.0; }
            if (dv > 4.5 && dv < 5.5) { glo = 539711.0; ghi = 14896.0; }
            if (dv > 5.5 && dv < 6.5) { glo = 492620.0; ghi = 14897.0; }
            if (dv > 6.5 && dv < 7.5) { glo = 139807.0; ghi = 2114.0; }
            if (dv > 7.5 && dv < 8.5) { glo = 476718.0; ghi = 14897.0; }
            if (dv > 8.5 && dv < 9.5) { glo = 1001006.0; ghi = 6416.0; }
        }
        if (ci > 5.5 && ci < 6.5)
        {
            float dv = clamp(floor(mod((13632.0 + Time), 60.0) / 10.0), 0.0, 9.0);
            if (dv > -0.5 && dv < 0.5) { glo = 714286.0; ghi = 14899.0; }
            if (dv > 0.5 && dv < 1.5) { glo = 135364.0; ghi = 14468.0; }
            if (dv > 1.5 && dv < 2.5) { glo = 279086.0; ghi = 31812.0; }
            if (dv > 2.5 && dv < 3.5) { glo = 266527.0; ghi = 14896.0; }
            if (dv > 3.5 && dv < 4.5) { glo = 305544.0; ghi = 8479.0; }
            if (dv > 4.5 && dv < 5.5) { glo = 539711.0; ghi = 14896.0; }
            if (dv > 5.5 && dv < 6.5) { glo = 492620.0; ghi = 14897.0; }
            if (dv > 6.5 && dv < 7.5) { glo = 139807.0; ghi = 2114.0; }
            if (dv > 7.5 && dv < 8.5) { glo = 476718.0; ghi = 14897.0; }
            if (dv > 8.5 && dv < 9.5) { glo = 1001006.0; ghi = 6416.0; }
        }
        if (ci > 6.5 && ci < 7.5)
        {
            float dv = clamp(floor(mod((13632.0 + Time), 10.0)), 0.0, 9.0);
            if (dv > -0.5 && dv < 0.5) { glo = 714286.0; ghi = 14899.0; }
            if (dv > 0.5 && dv < 1.5) { glo = 135364.0; ghi = 14468.0; }
            if (dv > 1.5 && dv < 2.5) { glo = 279086.0; ghi = 31812.0; }
            if (dv > 2.5 && dv < 3.5) { glo = 266527.0; ghi = 14896.0; }
            if (dv > 3.5 && dv < 4.5) { glo = 305544.0; ghi = 8479.0; }
            if (dv > 4.5 && dv < 5.5) { glo = 539711.0; ghi = 14896.0; }
            if (dv > 5.5 && dv < 6.5) { glo = 492620.0; ghi = 14897.0; }
            if (dv > 6.5 && dv < 7.5) { glo = 139807.0; ghi = 2114.0; }
            if (dv > 7.5 && dv < 8.5) { glo = 476718.0; ghi = 14897.0; }
            if (dv > 8.5 && dv < 9.5) { glo = 1001006.0; ghi = 6416.0; }
        }
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
    vec2 q = vec2((UV.x - 0.12) / 0.038668, (UV.y - 0.88) / 0.06);
    if (q.y >= 0.0 && q.y < 1.0 && q.x >= 0.0 && q.x < 3.0)
    {
        float ci = floor(q.x);
        float px = floor(fract(q.x) * 6.0);
        float py = floor(q.y * 7.0);
        float glo = 0.0;
        float ghi = 0.0;
        if (ci > -0.5 && ci < 0.5) { glo = 509487.0; ghi = 17701.0; }
        if (ci > 0.5 && ci < 1.5) { glo = 492607.0; ghi = 31777.0; }
        if (ci > 1.5 && ci < 2.5) { glo = 34350.0; ghi = 14881.0; }
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
    vec2 q = vec2((UV.x - 0.177766) / 0.064447, (UV.y - 0.72) / 0.1);
    if (q.y >= 0.0 && q.y < 1.0 && q.x >= 0.0 && q.x < 10.0)
    {
        float ci = floor(q.x);
        float px = floor(fract(q.x) * 6.0);
        float py = floor(q.y * 7.0);
        float glo = 0.0;
        float ghi = 0.0;
        if (ci > -0.5 && ci < 0.5) { glo = 135300.0; ghi = 4100.0; }
        if (ci > 1.5 && ci < 2.5) { glo = 710513.0; ghi = 17969.0; }
        if (ci > 2.5 && ci < 3.5) { glo = 575022.0; ghi = 14897.0; }
        if (ci > 3.5 && ci < 4.5) { glo = 135327.0; ghi = 4228.0; }
        if (ci > 4.5 && ci < 5.5) { glo = 135310.0; ghi = 14468.0; }
        if (ci > 5.5 && ci < 6.5) { glo = 575022.0; ghi = 14897.0; }
        if (ci > 6.5 && ci < 7.5) { glo = 708145.0; ghi = 17977.0; }
        if (ci > 8.5 && ci < 9.5) { glo = 135300.0; ghi = 4100.0; }
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
