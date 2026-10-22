$input v_worldPos, v_normal, v_tangent, v_bitangent, v_texcoord0, v_viewPos, v_objectPos, v_objectNormal

// Generated from Assets/ShaderGraphs/LaunchNight/CCTVServerRoom.shadergraph by the shader graph compiler: edit the graph, not this file.

#include "Common.sh"
#include "StandardSurface.sh"
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
	// Feed #14
	float n14_Gray;
	float n14_Fire;
	float n14_Backing;
	sgCustom_Feed_99340(n12_Out, sg_Time, vec2(0.620000005, 0.5), 1.0, n14_Gray, n14_Fire, n14_Backing);
	// Combine #25
	vec4 n25_RGBA = vec4(n14_Gray, n14_Gray, n14_Gray, 1.0);
	// Multiply #26
	vec3 n26_Out = n25_RGBA.xyz * vec3(0.800000012, 0.949999988, 0.850000024);
	// Multiply #28
	vec4 n28_Out = vec4_splat(n14_Fire) * vec4(7.5913291, 1.24277043, 0.0732389688, 1.0);
	// Add #29
	vec4 n29_Out = vec4(n26_Out, 1.0) + n28_Out;
	// Multiply #30
	float n30_Out = n14_Backing * 0.850000024;
	// One Minus #31
	float n31_Out = 1.0 - n30_Out;
	// Multiply #32
	vec4 n32_Out = n29_Out * vec4_splat(n31_Out);
	// Overlay #15
	float n15_Mask1;
	float n15_Mask2;
	float n15_Mask3;
	sgCustom_Overlay_91702(n12_Out, sg_Time, n15_Mask1, n15_Mask2, n15_Mask3);
	// Multiply #36
	vec4 n36_Out = vec4_splat(n15_Mask1) * vec4(0.787412345, 0.890005529, 0.787412345, 1.0);
	// Subtract #19
	vec2 n19_Out = n12_Out - vec2(0.075000003, 0.910000026);
	// Multiply #20
	vec2 n20_Out = n19_Out * vec2(1.33000004, 1.0);
	// Length #21
	float n21_Out = length(n20_Out);
	// Smoothstep #22
	float n22_Out = smoothstep(0.0120000001, 0.0219999999, n21_Out);
	// One Minus #23
	float n23_Out = 1.0 - n22_Out;
	// Multiply #16
	float n16_Out = sg_Time * 1.10000002;
	// Fraction #17
	float n17_Out = fract(n16_Out);
	// Step #18
	float n18_Out = step(0.5, n17_Out);
	// Multiply #24
	float n24_Out = n23_Out * n18_Out;
	// Add #33
	float n33_Out = n15_Mask2 + n24_Out;
	// Multiply #38
	vec4 n38_Out = vec4_splat(n33_Out) * vec4(2.94651985, 0.0134117464, 0.00489630876, 1.0);
	// Add #39
	vec4 n39_Out = n36_Out + n38_Out;
	// Multiply #34
	float n34_Out = n15_Mask3 * n18_Out;
	// Multiply #41
	vec4 n41_Out = vec4_splat(n34_Out) * vec4(9.161129, 0.0331047624, 0.0100228256, 1.0);
	// Add #42
	vec4 n42_Out = n39_Out + n41_Out;
	// Add #43
	vec4 n43_Out = n32_Out + n42_Out;
	// Split #44
	vec2 n44_In = n12_Out;
	// Multiply #45
	float n45_Out = n44_In.y * 900.0;
	// Sine #46
	float n46_Out = sin(n45_Out);
	// Multiply #47
	float n47_Out = n46_Out * 0.119999997;
	// Add #48
	float n48_Out = 0.879999995 + n47_Out;
	// Subtract #49
	vec2 n49_Out = n12_Out - vec2(0.5, 0.5);
	// Length #50
	float n50_Out = length(n49_Out);
	// Remap #51
	float n51_Out = 1.0 + (n50_Out - 0.349999994) * (0.550000012 - 1.0) / (0.75 - 0.349999994);
	// Saturate #52
	float n52_Out = clamp(n51_Out, 0.0, 1.0);
	// Multiply #53
	float n53_Out = n48_Out * n52_Out;
	// Multiply #54
	vec4 n54_Out = n43_Out * vec4_splat(n53_Out);
	// Step #56
	float n56_Out = step(0.0, n44_In.x);
	// Step #57
	float n57_Out = step(n44_In.x, 1.0);
	// Multiply #58
	float n58_Out = n56_Out * n57_Out;
	// Step #59
	float n59_Out = step(0.0, n44_In.y);
	// Step #60
	float n60_Out = step(n44_In.y, 1.0);
	// Multiply #61
	float n61_Out = n59_Out * n60_Out;
	// Multiply #62
	float n62_Out = n58_Out * n61_Out;
	// Multiply #63
	float n63_Out = u_sgParams[0].x * n62_Out;
	// Multiply #64
	vec4 n64_Out = n54_Out * vec4_splat(n63_Out);
	// Outputs
	vec3 sgOut_BaseColor = vec3(0.00999999978, 0.00999999978, 0.0120000001);
	vec3 sgOut_Normal = vec3(0.0, 0.0, 1.0);
	float sgOut_Metallic = 0.0;
	float sgOut_Roughness = 0.300000012;
	vec3 sgOut_Emission = (n64_Out).xyz;
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
