$input v_worldPos, v_normal, v_tangent, v_bitangent, v_texcoord0, v_viewPos, v_objectPos, v_objectNormal

// Generated from Assets/ShaderGraphs/LaunchNight/BuildStatus.shadergraph by the shader graph compiler: edit the graph, not this file.

#include "Common.sh"
#include "StandardSurface.sh"
#include "ShaderGraph/SGLib.sh"

uniform vec4 u_sgParams[16];
// u_sgParams[0]: Brightness (Float)
// u_sgParams[1]: UV Rect (Vector 4)
// u_sgParams[2]: Flip (Vector 2)

void sgCustom_BuildStatus_70351(vec2 UV, out float Mask1, out float Mask2, out float Mask3)
{
Mask1 = 0.0;
Mask2 = 0.0;
Mask3 = 0.0;
{
    vec2 q = vec2((UV.x - 0.05) / 0.033835, (UV.y - 0.06) / 0.06);
    if (q.y >= 0.0 && q.y < 1.0 && q.x >= 0.0 && q.x < 11.0)
    {
        float ci = floor(q.x);
        float px = floor(fract(q.x) * 6.0);
        float py = floor(q.y * 7.0);
        float glo = 0.0;
        float ghi = 0.0;
        if (ci > -0.5 && ci < 0.5) { glo = 710513.0; ghi = 17969.0; }
        if (ci > 0.5 && ci < 1.5) { glo = 575022.0; ghi = 14897.0; }
        if (ci > 1.5 && ci < 2.5) { glo = 575022.0; ghi = 14897.0; }
        if (ci > 2.5 && ci < 3.5) { glo = 708145.0; ghi = 17977.0; }
        if (ci > 3.5 && ci < 4.5) { glo = 459838.0; ghi = 15888.0; }
        if (ci > 4.5 && ci < 5.5) { glo = 1033777.0; ghi = 17969.0; }
        if (ci > 5.5 && ci < 6.5) { glo = 575022.0; ghi = 14897.0; }
        if (ci > 6.5 && ci < 7.5) { glo = 135327.0; ghi = 4228.0; }
        if (ci > 8.5 && ci < 9.5) { glo = 34350.0; ghi = 14881.0; }
        if (ci > 9.5 && ci < 10.5) { glo = 135310.0; ghi = 14468.0; }
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
    vec2 q = vec2((UV.x - 0.05) / 0.056391, (UV.y - 0.16) / 0.1);
    if (q.y >= 0.0 && q.y < 1.0 && q.x >= 0.0 && q.x < 11.0)
    {
        float ci = floor(q.x);
        float px = floor(fract(q.x) * 6.0);
        float py = floor(q.y * 7.0);
        float glo = 0.0;
        float ghi = 0.0;
        if (ci > -0.5 && ci < 0.5) { glo = 509487.0; ghi = 15921.0; }
        if (ci > 0.5 && ci < 1.5) { glo = 575025.0; ghi = 14897.0; }
        if (ci > 1.5 && ci < 2.5) { glo = 135310.0; ghi = 14468.0; }
        if (ci > 2.5 && ci < 3.5) { glo = 33825.0; ghi = 31777.0; }
        if (ci > 3.5 && ci < 4.5) { glo = 575023.0; ghi = 15921.0; }
        if (ci > 5.5 && ci < 6.5) { glo = 359754.0; ghi = 10591.0; }
        if (ci > 6.5 && ci < 7.5) { glo = 305544.0; ghi = 8479.0; }
        if (ci > 7.5 && ci < 8.5) { glo = 305544.0; ghi = 8479.0; }
        if (ci > 8.5 && ci < 9.5) { glo = 139807.0; ghi = 2114.0; }
        if (ci > 9.5 && ci < 10.5) { glo = 135364.0; ghi = 14468.0; }
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
    vec2 q = vec2((UV.x - 0.05) / 0.112782, (UV.y - 0.31) / 0.2);
    if (q.y >= 0.0 && q.y < 1.0 && q.x >= 0.0 && q.x < 6.0)
    {
        float ci = floor(q.x);
        float px = floor(fract(q.x) * 6.0);
        float py = floor(q.y * 7.0);
        float glo = 0.0;
        float ghi = 0.0;
        if (ci > -0.5 && ci < 0.5) { glo = 492607.0; ghi = 1057.0; }
        if (ci > 0.5 && ci < 1.5) { glo = 1033774.0; ghi = 17969.0; }
        if (ci > 1.5 && ci < 2.5) { glo = 135310.0; ghi = 14468.0; }
        if (ci > 2.5 && ci < 3.5) { glo = 33825.0; ghi = 31777.0; }
        if (ci > 3.5 && ci < 4.5) { glo = 492607.0; ghi = 31777.0; }
        if (ci > 4.5 && ci < 5.5) { glo = 575023.0; ghi = 15921.0; }
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
    vec2 q = vec2((UV.x - 0.05) / 0.033835, (UV.y - 0.58) / 0.06);
    if (q.y >= 0.0 && q.y < 1.0 && q.x >= 0.0 && q.x < 7.0)
    {
        float ci = floor(q.x);
        float px = floor(fract(q.x) * 6.0);
        float py = floor(q.y * 7.0);
        float glo = 0.0;
        float ghi = 0.0;
        if (ci > -0.5 && ci < 0.5) { glo = 34350.0; ghi = 14881.0; }
        if (ci > 0.5 && ci < 1.5) { glo = 575022.0; ghi = 14897.0; }
        if (ci > 1.5 && ci < 2.5) { glo = 710513.0; ghi = 17969.0; }
        if (ci > 2.5 && ci < 3.5) { glo = 509487.0; ghi = 1057.0; }
        if (ci > 3.5 && ci < 4.5) { glo = 135310.0; ghi = 14468.0; }
        if (ci > 4.5 && ci < 5.5) { glo = 33825.0; ghi = 31777.0; }
        if (ci > 5.5 && ci < 6.5) { glo = 492607.0; ghi = 31777.0; }
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
    vec2 q = vec2((UV.x - 0.42) / 0.033835, (UV.y - 0.58) / 0.06);
    if (q.y >= 0.0 && q.y < 1.0 && q.x >= 0.0 && q.x < 2.0)
    {
        float ci = floor(q.x);
        float px = floor(fract(q.x) * 6.0);
        float py = floor(q.y * 7.0);
        float glo = 0.0;
        float ghi = 0.0;
        if (ci > -0.5 && ci < 0.5) { glo = 575022.0; ghi = 14897.0; }
        if (ci > 0.5 && ci < 1.5) { glo = 103729.0; ghi = 17701.0; }
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
    vec2 q = vec2((UV.x - 0.05) / 0.033835, (UV.y - 0.66) / 0.06);
    if (q.y >= 0.0 && q.y < 1.0 && q.x >= 0.0 && q.x < 11.0)
    {
        float ci = floor(q.x);
        float px = floor(fract(q.x) * 6.0);
        float py = floor(q.y * 7.0);
        float glo = 0.0;
        float ghi = 0.0;
        if (ci > -0.5 && ci < 0.5) { glo = 34350.0; ghi = 14881.0; }
        if (ci > 0.5 && ci < 1.5) { glo = 575022.0; ghi = 14897.0; }
        if (ci > 1.5 && ci < 2.5) { glo = 575022.0; ghi = 14897.0; }
        if (ci > 2.5 && ci < 3.5) { glo = 103729.0; ghi = 17701.0; }
        if (ci > 4.5 && ci < 5.5) { glo = 1033774.0; ghi = 17969.0; }
        if (ci > 5.5 && ci < 6.5) { glo = 459838.0; ghi = 15888.0; }
        if (ci > 6.5 && ci < 7.5) { glo = 459838.0; ghi = 15888.0; }
        if (ci > 7.5 && ci < 8.5) { glo = 492607.0; ghi = 31777.0; }
        if (ci > 8.5 && ci < 9.5) { glo = 135327.0; ghi = 4228.0; }
        if (ci > 9.5 && ci < 10.5) { glo = 459838.0; ghi = 15888.0; }
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
    vec2 q = vec2((UV.x - 0.42) / 0.033835, (UV.y - 0.66) / 0.06);
    if (q.y >= 0.0 && q.y < 1.0 && q.x >= 0.0 && q.x < 2.0)
    {
        float ci = floor(q.x);
        float px = floor(fract(q.x) * 6.0);
        float py = floor(q.y * 7.0);
        float glo = 0.0;
        float ghi = 0.0;
        if (ci > -0.5 && ci < 0.5) { glo = 575022.0; ghi = 14897.0; }
        if (ci > 0.5 && ci < 1.5) { glo = 103729.0; ghi = 17701.0; }
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
    vec2 q = vec2((UV.x - 0.05) / 0.033835, (UV.y - 0.74) / 0.06);
    if (q.y >= 0.0 && q.y < 1.0 && q.x >= 0.0 && q.x < 10.0)
    {
        float ci = floor(q.x);
        float px = floor(fract(q.x) * 6.0);
        float py = floor(q.y * 7.0);
        float glo = 0.0;
        float ghi = 0.0;
        if (ci > -0.5 && ci < 0.5) { glo = 575025.0; ghi = 14897.0; }
        if (ci > 0.5 && ci < 1.5) { glo = 708145.0; ghi = 17977.0; }
        if (ci > 1.5 && ci < 2.5) { glo = 135310.0; ghi = 14468.0; }
        if (ci > 2.5 && ci < 3.5) { glo = 135327.0; ghi = 4228.0; }
        if (ci > 4.5 && ci < 5.5) { glo = 135327.0; ghi = 4228.0; }
        if (ci > 5.5 && ci < 6.5) { glo = 492607.0; ghi = 31777.0; }
        if (ci > 6.5 && ci < 7.5) { glo = 459838.0; ghi = 15888.0; }
        if (ci > 7.5 && ci < 8.5) { glo = 135327.0; ghi = 4228.0; }
        if (ci > 8.5 && ci < 9.5) { glo = 459838.0; ghi = 15888.0; }
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
    vec2 q = vec2((UV.x - 0.42) / 0.033835, (UV.y - 0.74) / 0.06);
    if (q.y >= 0.0 && q.y < 1.0 && q.x >= 0.0 && q.x < 8.0)
    {
        float ci = floor(q.x);
        float px = floor(fract(q.x) * 6.0);
        float py = floor(q.y * 7.0);
        float glo = 0.0;
        float ghi = 0.0;
        if (ci > -0.5 && ci < 0.5) { glo = 476718.0; ghi = 14897.0; }
        if (ci > 0.5 && ci < 1.5) { glo = 305544.0; ghi = 8479.0; }
        if (ci > 1.5 && ci < 2.5) { glo = 139807.0; ghi = 2114.0; }
        if (ci > 3.5 && ci < 4.5) { glo = 492607.0; ghi = 1057.0; }
        if (ci > 4.5 && ci < 5.5) { glo = 1033774.0; ghi = 17969.0; }
        if (ci > 5.5 && ci < 6.5) { glo = 135310.0; ghi = 14468.0; }
        if (ci > 6.5 && ci < 7.5) { glo = 33825.0; ghi = 31777.0; }
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
    vec2 q = vec2((UV.x - 0.05) / 0.033835, (UV.y - 0.82) / 0.06);
    if (q.y >= 0.0 && q.y < 1.0 && q.x >= 0.0 && q.x < 11.0)
    {
        float ci = floor(q.x);
        float px = floor(fract(q.x) * 6.0);
        float py = floor(q.y * 7.0);
        float glo = 0.0;
        float ghi = 0.0;
        if (ci > -0.5 && ci < 0.5) { glo = 509487.0; ghi = 15921.0; }
        if (ci > 0.5 && ci < 1.5) { glo = 575025.0; ghi = 14897.0; }
        if (ci > 1.5 && ci < 2.5) { glo = 135310.0; ghi = 14468.0; }
        if (ci > 2.5 && ci < 3.5) { glo = 33825.0; ghi = 31777.0; }
        if (ci > 3.5 && ci < 4.5) { glo = 575023.0; ghi = 15921.0; }
        if (ci > 5.5 && ci < 6.5) { glo = 1033774.0; ghi = 17969.0; }
        if (ci > 6.5 && ci < 7.5) { glo = 951854.0; ghi = 31281.0; }
        if (ci > 7.5 && ci < 8.5) { glo = 492607.0; ghi = 31777.0; }
        if (ci > 8.5 && ci < 9.5) { glo = 708145.0; ghi = 17977.0; }
        if (ci > 9.5 && ci < 10.5) { glo = 135327.0; ghi = 4228.0; }
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
    vec2 q = vec2((UV.x - 0.42) / 0.033835, (UV.y - 0.82) / 0.06);
    if (q.y >= 0.0 && q.y < 1.0 && q.x >= 0.0 && q.x < 7.0)
    {
        float ci = floor(q.x);
        float px = floor(fract(q.x) * 6.0);
        float py = floor(q.y * 7.0);
        float glo = 0.0;
        float ghi = 0.0;
        if (ci > -0.5 && ci < 0.5) { glo = 575022.0; ghi = 14897.0; }
        if (ci > 0.5 && ci < 1.5) { glo = 708145.0; ghi = 17977.0; }
        if (ci > 2.5 && ci < 3.5) { glo = 492607.0; ghi = 1057.0; }
        if (ci > 3.5 && ci < 4.5) { glo = 135310.0; ghi = 14468.0; }
        if (ci > 4.5 && ci < 5.5) { glo = 509487.0; ghi = 17701.0; }
        if (ci > 5.5 && ci < 6.5) { glo = 492607.0; ghi = 31777.0; }
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
    vec2 q = vec2((UV.x - 0.05) / 0.025376, (UV.y - 0.92) / 0.045);
    if (q.y >= 0.0 && q.y < 1.0 && q.x >= 0.0 && q.x < 22.0)
    {
        float ci = floor(q.x);
        float px = floor(fract(q.x) * 6.0);
        float py = floor(q.y * 7.0);
        float glo = 0.0;
        float ghi = 0.0;
        if (ci > -0.5 && ci < 0.5) { glo = 33825.0; ghi = 31777.0; }
        if (ci > 0.5 && ci < 1.5) { glo = 1033774.0; ghi = 17969.0; }
        if (ci > 1.5 && ci < 2.5) { glo = 459838.0; ghi = 15888.0; }
        if (ci > 2.5 && ci < 3.5) { glo = 135327.0; ghi = 4228.0; }
        if (ci > 4.5 && ci < 5.5) { glo = 951854.0; ghi = 31281.0; }
        if (ci > 5.5 && ci < 6.5) { glo = 509487.0; ghi = 17701.0; }
        if (ci > 6.5 && ci < 7.5) { glo = 492607.0; ghi = 31777.0; }
        if (ci > 7.5 && ci < 8.5) { glo = 492607.0; ghi = 31777.0; }
        if (ci > 8.5 && ci < 9.5) { glo = 708145.0; ghi = 17977.0; }
        if (ci > 9.5 && ci < 10.5) { glo = 6336.0; ghi = 198.0; }
        if (ci > 11.5 && ci < 12.5) { glo = 266527.0; ghi = 14896.0; }
        if (ci > 13.5 && ci < 14.5) { glo = 575023.0; ghi = 15921.0; }
        if (ci > 14.5 && ci < 15.5) { glo = 1033774.0; ghi = 17969.0; }
        if (ci > 15.5 && ci < 16.5) { glo = 141873.0; ghi = 4228.0; }
        if (ci > 16.5 && ci < 17.5) { glo = 459838.0; ghi = 15888.0; }
        if (ci > 18.5 && ci < 19.5) { glo = 1033774.0; ghi = 17969.0; }
        if (ci > 19.5 && ci < 20.5) { glo = 951854.0; ghi = 31281.0; }
        if (ci > 20.5 && ci < 21.5) { glo = 575022.0; ghi = 14897.0; }
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
    vec2 q = vec2((UV.x - 0.66) / 0.028195, (UV.y - 0.2) / 0.05);
    if (q.y >= 0.0 && q.y < 1.0 && q.x >= 0.0 && q.x < 10.0)
    {
        float ci = floor(q.x);
        float px = floor(fract(q.x) * 6.0);
        float py = floor(q.y * 7.0);
        float glo = 0.0;
        float ghi = 0.0;
        if (ci > -0.5 && ci < 0.5) { glo = 575023.0; ghi = 15921.0; }
        if (ci > 0.5 && ci < 1.5) { glo = 1033774.0; ghi = 17969.0; }
        if (ci > 1.5 && ci < 2.5) { glo = 141873.0; ghi = 4228.0; }
        if (ci > 2.5 && ci < 3.5) { glo = 459838.0; ghi = 15888.0; }
        if (ci > 4.5 && ci < 5.5) { glo = 459838.0; ghi = 15888.0; }
        if (ci > 5.5 && ci < 6.5) { glo = 135310.0; ghi = 14468.0; }
        if (ci > 6.5 && ci < 7.5) { glo = 708145.0; ghi = 17977.0; }
        if (ci > 7.5 && ci < 8.5) { glo = 34350.0; ghi = 14881.0; }
        if (ci > 8.5 && ci < 9.5) { glo = 492607.0; ghi = 31777.0; }
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
    vec2 q = vec2((UV.x - 0.66) / 0.028195, (UV.y - 0.27) / 0.05);
    if (q.y >= 0.0 && q.y < 1.0 && q.x >= 0.0 && q.x < 9.0)
    {
        float ci = floor(q.x);
        float px = floor(fract(q.x) * 6.0);
        float py = floor(q.y * 7.0);
        float glo = 0.0;
        float ghi = 0.0;
        if (ci > -0.5 && ci < 0.5) { glo = 33825.0; ghi = 31777.0; }
        if (ci > 0.5 && ci < 1.5) { glo = 1033774.0; ghi = 17969.0; }
        if (ci > 1.5 && ci < 2.5) { glo = 459838.0; ghi = 15888.0; }
        if (ci > 2.5 && ci < 3.5) { glo = 135327.0; ghi = 4228.0; }
        if (ci > 4.5 && ci < 5.5) { glo = 492607.0; ghi = 1057.0; }
        if (ci > 5.5 && ci < 6.5) { glo = 135310.0; ghi = 14468.0; }
        if (ci > 6.5 && ci < 7.5) { glo = 509487.0; ghi = 17701.0; }
        if (ci > 7.5 && ci < 8.5) { glo = 492607.0; ghi = 31777.0; }
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

void sgCustom_DaysSince_38244(vec2 UV, out float Mask1, out float Mask2, out float Mask3)
{
Mask1 = 0.0;
Mask2 = 0.0;
Mask3 = 0.0;
{
    vec2 q = vec2((UV.x - 0.73) / 0.180451, (UV.y - 0.38) / 0.32);
    if (q.y >= 0.0 && q.y < 1.0 && q.x >= 0.0 && q.x < 1.0)
    {
        float ci = floor(q.x);
        float px = floor(fract(q.x) * 6.0);
        float py = floor(q.y * 7.0);
        float glo = 0.0;
        float ghi = 0.0;
        if (ci > -0.5 && ci < 0.5) { glo = 714286.0; ghi = 14899.0; }
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
	vec4 sg_fragCoord = gl_FragCoord;
	bool sg_frontFacing = gl_FrontFacing;
	vec2 sg_UV0 = v_texcoord0;
	float sg_Time = u_time.y;
	float sg_DeltaTime = u_time.x;

	// Swizzle .xy #5
	vec2 n5_Out = (u_sgParams[1]).xy;
	// Subtract #8
	vec2 n8_Out = sg_UV0 - n5_Out;
	// Swizzle .zw #6
	vec2 n6_Out = (u_sgParams[1]).zw;
	// Subtract #9
	vec2 n9_Out = n6_Out - n5_Out;
	// Divide #10
	vec2 n10_Out = n8_Out / n9_Out;
	// Subtract #11
	vec2 n11_Out = vec2(1.0, 1.0) - n10_Out;
	// Lerp #12
	vec2 n12_Out = mix(n10_Out, n11_Out, u_sgParams[2].xy);
	// BuildStatus #13
	float n13_Mask1;
	float n13_Mask2;
	float n13_Mask3;
	sgCustom_BuildStatus_70351(n12_Out, n13_Mask1, n13_Mask2, n13_Mask3);
	// Multiply #41
	vec4 n41_Out = vec4_splat(n13_Mask1) * vec4(0.787412345, 0.827570975, 0.890005529, 1.0);
	// Multiply #16
	float n16_Out = sg_Time * 0.899999976;
	// Fraction #17
	float n17_Out = fract(n16_Out);
	// Step #18
	float n18_Out = step(0.449999988, n17_Out);
	// Multiply #19
	float n19_Out = n18_Out * 0.649999976;
	// Add #20
	float n20_Out = 0.349999994 + n19_Out;
	// Multiply #39
	float n39_Out = n13_Mask2 * n20_Out;
	// Multiply #43
	vec4 n43_Out = vec4_splat(n39_Out) * vec4(1.0, 0.0100228256, 0.00309597515, 1.0);
	// Add #44
	vec4 n44_Out = n41_Out + n43_Out;
	// Multiply #46
	vec4 n46_Out = vec4_splat(n13_Mask3) * vec4(0.0196066499, 1.0, 0.100481518, 1.0);
	// Add #47
	vec4 n47_Out = n44_Out + n46_Out;
	// DaysSince #14
	float n14_Mask1;
	float n14_Mask2;
	float n14_Mask3;
	sgCustom_DaysSince_38244(n12_Out, n14_Mask1, n14_Mask2, n14_Mask3);
	// Multiply #49
	vec4 n49_Out = vec4_splat(n14_Mask1) * vec4(1.0, 0.522521615, 0.0100228256, 1.0);
	// Split #21
	vec2 n21_In = n12_Out;
	// Step #22
	float n22_Out = step(0.620000005, n21_In.x);
	// Step #23
	float n23_Out = step(n21_In.x, 0.949999988);
	// Multiply #24
	float n24_Out = n22_Out * n23_Out;
	// Step #25
	float n25_Out = step(0.569999993, n21_In.y);
	// Multiply #26
	float n26_Out = n24_Out * n25_Out;
	// Step #27
	float n27_Out = step(n21_In.y, 0.879999995);
	// Multiply #28
	float n28_Out = n26_Out * n27_Out;
	// Subtract #29
	float n29_Out = n21_In.y - 0.569999993;
	// Multiply #30
	float n30_Out = n29_Out * 12.5;
	// Fraction #31
	float n31_Out = fract(n30_Out);
	// Step #32
	float n32_Out = step(n31_Out, 0.699999988);
	// Multiply #33
	float n33_Out = n28_Out * n32_Out;
	// Multiply #37
	vec4 n37_Out = vec4(1.0, 0.0100228256, 0.00393593963, 1.0) * vec4_splat(n20_Out);
	// Step #34
	float n34_Out = step(0.720000029, n21_In.y);
	// Lerp #38
	vec4 n38_Out = mix(vec4(0.0100228256, 0.787412345, 0.0732389688, 1.0), n37_Out, vec4_splat(n34_Out));
	// Multiply #50
	vec4 n50_Out = vec4_splat(n33_Out) * n38_Out;
	// Add #51
	vec4 n51_Out = n49_Out + n50_Out;
	// Add #52
	vec4 n52_Out = n47_Out + n51_Out;
	// Multiply #55
	float n55_Out = n20_Out * 0.5;
	// Lerp #56
	vec4 n56_Out = mix(vec4(0.00232198136, 0.00270897825, 0.00393593963, 1.0), vec4(0.0134117464, 0.000773993786, 0.000773993786, 1.0), vec4_splat(n55_Out));
	// Add #57
	vec4 n57_Out = n52_Out + n56_Out;
	// Multiply #59
	float n59_Out = n21_In.y * 900.0;
	// Sine #60
	float n60_Out = sin(n59_Out);
	// Multiply #61
	float n61_Out = n60_Out * 0.119999997;
	// Add #62
	float n62_Out = 0.879999995 + n61_Out;
	// Subtract #63
	vec2 n63_Out = n12_Out - vec2(0.5, 0.5);
	// Length #64
	float n64_Out = length(n63_Out);
	// Remap #65
	float n65_Out = 1.0 + (n64_Out - 0.349999994) * (0.550000012 - 1.0) / (0.75 - 0.349999994);
	// Saturate #66
	float n66_Out = clamp(n65_Out, 0.0, 1.0);
	// Multiply #67
	float n67_Out = n62_Out * n66_Out;
	// Multiply #68
	vec4 n68_Out = n57_Out * vec4_splat(n67_Out);
	// Step #70
	float n70_Out = step(0.0, n21_In.x);
	// Step #71
	float n71_Out = step(n21_In.x, 1.0);
	// Multiply #72
	float n72_Out = n70_Out * n71_Out;
	// Step #73
	float n73_Out = step(0.0, n21_In.y);
	// Step #74
	float n74_Out = step(n21_In.y, 1.0);
	// Multiply #75
	float n75_Out = n73_Out * n74_Out;
	// Multiply #76
	float n76_Out = n72_Out * n75_Out;
	// Multiply #77
	float n77_Out = u_sgParams[0].x * n76_Out;
	// Multiply #78
	vec4 n78_Out = n68_Out * vec4_splat(n77_Out);
	// Outputs
	vec3 sgOut_BaseColor = vec3(0.00999999978, 0.00999999978, 0.0120000001);
	vec3 sgOut_Normal = vec3(0.0, 0.0, 1.0);
	float sgOut_Metallic = 0.0;
	float sgOut_Roughness = 0.300000012;
	vec3 sgOut_Emission = (n78_Out).xyz;
	float sgOut_Occlusion = 0.119999997;
	float sgOut_Alpha = 1.0;
	float sgOut_AlphaClipThreshold = 0.5;

#if SG_ALPHA_CLIP
	if (sgOut_Alpha < sgOut_AlphaClipThreshold)
	{
		discard;
	}
#endif

#if SG_NORMAL_WORLD
	vec3 N = sgSafeNormalize(sgOut_Normal);
#else
	vec3 N = sgSafeNormalize(v_normal);
	if (dot(v_tangent, v_tangent) > 1e-6 && dot(v_bitangent, v_bitangent) > 1e-6)
	{
		mat3 TBN = mtxFromCols(normalize(v_tangent), normalize(v_bitangent), N);
		N = sgSafeNormalize(mul(TBN, sgOut_Normal));
	}
#endif

	SurfaceInput surface;
	surface.baseColor = sgOut_BaseColor;
	surface.alpha = sgOut_Alpha;
	surface.normal = N;
	surface.metallic = sgOut_Metallic;
	surface.roughness = sgOut_Roughness;
	surface.occlusion = sgOut_Occlusion;
	surface.emissive = sgOut_Emission;
	surface.uv = v_texcoord0;
	gl_FragColor = shadeStandardSurface(surface, v_worldPos, v_normal, v_viewPos, sg_fragCoord.xy, sg_frontFacing);
}
