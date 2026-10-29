$input v_worldPos, v_normal, v_tangent, v_bitangent, v_texcoord0, v_viewPos, v_objectPos, v_objectNormal

// Generated from Assets/ShaderGraphs/LaunchNight/Countdown.shadergraph by the shader graph compiler: edit the graph, not this file.

#include "Common.sh"
#include "StandardSurface.sh"
#include "ShaderGraph/SGLib.sh"
#include "Dither.sh"

uniform vec4 u_drawParams; // x screen-door fade (Dither.sh), per draw

uniform vec4 u_sgParams[16];
// u_sgParams[0]: Start Seconds (Float)
// u_sgParams[1]: Brightness (Float)
// u_sgParams[2]: UV Rect (Vector 4)
// u_sgParams[3]: Flip (Vector 2)

void sgCustom_Countdown_33437(vec2 UV, float Time, float Start, out float Mask1, out float Mask2, out float Mask3)
{
Mask1 = 0.0;
Mask2 = 0.0;
Mask3 = 0.0;
{
    vec2 q = vec2((UV.x - 0.105263) / 0.056391, (UV.y - 0.13) / 0.1);
    if (q.y >= 0.0 && q.y < 1.0 && q.x >= 0.0 && q.x < 14.0)
    {
        float ci = floor(q.x);
        float px = floor(fract(q.x) * 6.0);
        float py = floor(q.y * 7.0);
        float glo = 0.0;
        float ghi = 0.0;
        if (ci > -0.5 && ci < 0.5) { glo = 951854.0; ghi = 31281.0; }
        if (ci > 0.5 && ci < 1.5) { glo = 575022.0; ghi = 14897.0; }
        if (ci > 1.5 && ci < 2.5) { glo = 33825.0; ghi = 31777.0; }
        if (ci > 2.5 && ci < 3.5) { glo = 575023.0; ghi = 15921.0; }
        if (ci > 4.5 && ci < 5.5) { glo = 710513.0; ghi = 17969.0; }
        if (ci > 5.5 && ci < 6.5) { glo = 1033774.0; ghi = 17969.0; }
        if (ci > 6.5 && ci < 7.5) { glo = 459838.0; ghi = 15888.0; }
        if (ci > 7.5 && ci < 8.5) { glo = 135327.0; ghi = 4228.0; }
        if (ci > 8.5 && ci < 9.5) { glo = 492607.0; ghi = 31777.0; }
        if (ci > 9.5 && ci < 10.5) { glo = 509487.0; ghi = 17701.0; }
        if (ci > 11.5 && ci < 12.5) { glo = 135310.0; ghi = 14468.0; }
        if (ci > 12.5 && ci < 13.5) { glo = 708145.0; ghi = 17977.0; }
        float hit = 0.0;
        if (px < 5.0)

        {
            float b = py * 5.0 + px;
            float word = b < 20.0 ? glo : ghi;
            float shift = b < 20.0 ? b : b - 20.0;
            hit = mod(floor(word / exp2(shift)), 2.0);
        }
        
        vec2 sub = vec2(fract(fract(q.x) * 6.0), fract(q.y * 7.0)) - vec2_splat(0.5);
        hit *= 1.0 - smoothstep(0.3, 0.46, length(sub));
        Mask1 = max(Mask1, hit);
    }
}
{
    vec2 q = vec2((UV.x - 0.071429) / 0.107143, (UV.y - 0.36) / 0.19);
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
            float dv = clamp(floor(max(Start - Time, 0.0) / 36000.0), 0.0, 9.0);
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
            float dv = clamp(floor(mod(max(Start - Time, 0.0) / 3600.0, 10.0)), 0.0, 9.0);
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
            float dv = clamp(floor(mod(max(Start - Time, 0.0), 3600.0) / 600.0), 0.0, 9.0);
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
            float dv = clamp(floor(mod(mod(max(Start - Time, 0.0), 3600.0) / 60.0, 10.0)), 0.0, 9.0);
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
            float dv = clamp(floor(mod(max(Start - Time, 0.0), 60.0) / 10.0), 0.0, 9.0);
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
            float dv = clamp(floor(mod(max(Start - Time, 0.0), 10.0)), 0.0, 9.0);
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
        
        vec2 sub = vec2(fract(fract(q.x) * 6.0), fract(q.y * 7.0)) - vec2_splat(0.5);
        hit *= 1.0 - smoothstep(0.3, 0.46, length(sub));
        Mask2 = max(Mask2, hit);
    }
}
{
    vec2 q = vec2((UV.x - 0.085526) / 0.039474, (UV.y - 0.8) / 0.07);
    if (q.y >= 0.0 && q.y < 1.0 && q.x >= 0.0 && q.x < 21.0)
    {
        float ci = floor(q.x);
        float px = floor(fract(q.x) * 6.0);
        float py = floor(q.y * 7.0);
        float glo = 0.0;
        float ghi = 0.0;
        if (ci > -0.5 && ci < 0.5) { glo = 509487.0; ghi = 1057.0; }
        if (ci > 0.5 && ci < 1.5) { glo = 509487.0; ghi = 17701.0; }
        if (ci > 1.5 && ci < 2.5) { glo = 575022.0; ghi = 14897.0; }
        if (ci > 2.5 && ci < 3.5) { glo = 270620.0; ghi = 6440.0; }
        if (ci > 3.5 && ci < 4.5) { glo = 492607.0; ghi = 31777.0; }
        if (ci > 4.5 && ci < 5.5) { glo = 34350.0; ghi = 14881.0; }
        if (ci > 5.5 && ci < 6.5) { glo = 135327.0; ghi = 4228.0; }
        if (ci > 7.5 && ci < 8.5) { glo = 710513.0; ghi = 17969.0; }
        if (ci > 8.5 && ci < 9.5) { glo = 575022.0; ghi = 14897.0; }
        if (ci > 9.5 && ci < 10.5) { glo = 575022.0; ghi = 14897.0; }
        if (ci > 10.5 && ci < 11.5) { glo = 708145.0; ghi = 17977.0; }
        if (ci > 11.5 && ci < 12.5) { glo = 459838.0; ghi = 15888.0; }
        if (ci > 12.5 && ci < 13.5) { glo = 1033777.0; ghi = 17969.0; }
        if (ci > 13.5 && ci < 14.5) { glo = 575022.0; ghi = 14897.0; }
        if (ci > 14.5 && ci < 15.5) { glo = 135327.0; ghi = 4228.0; }
        if (ci > 16.5 && ci < 17.5) { glo = 575025.0; ghi = 4433.0; }
        if (ci > 17.5 && ci < 18.5) { glo = 135364.0; ghi = 14468.0; }
        if (ci > 18.5 && ci < 19.5) { glo = 0.0; ghi = 6336.0; }
        if (ci > 19.5 && ci < 20.5) { glo = 714286.0; ghi = 14899.0; }
        float hit = 0.0;
        if (px < 5.0)

        {
            float b = py * 5.0 + px;
            float word = b < 20.0 ? glo : ghi;
            float shift = b < 20.0 ? b : b - 20.0;
            hit = mod(floor(word / exp2(shift)), 2.0);
        }
        
        vec2 sub = vec2(fract(fract(q.x) * 6.0), fract(q.y * 7.0)) - vec2_splat(0.5);
        hit *= 1.0 - smoothstep(0.3, 0.46, length(sub));
        Mask3 = max(Mask3, hit);
    }
}
}


void main()
{
	if (ditherDrops(u_drawParams.x, gl_FragCoord.xy))
	{
		discard;
	}
	vec4 sg_fragCoord = gl_FragCoord;
	bool sg_frontFacing = gl_FrontFacing;
	vec2 sg_UV0 = v_texcoord0;
	float sg_Time = u_time.y;
	float sg_DeltaTime = u_time.x;

	// Swizzle .xy #6
	vec2 n6_Out = (u_sgParams[2]).xy;
	// Subtract #9
	vec2 n9_Out = sg_UV0 - n6_Out;
	// Swizzle .zw #7
	vec2 n7_Out = (u_sgParams[2]).zw;
	// Subtract #10
	vec2 n10_Out = n7_Out - n6_Out;
	// Divide #11
	vec2 n11_Out = n9_Out / n10_Out;
	// Subtract #12
	vec2 n12_Out = vec2(1.0, 1.0) - n11_Out;
	// Lerp #13
	vec2 n13_Out = mix(n11_Out, n12_Out, u_sgParams[3].xy);
	// Countdown #15
	float n15_Mask1;
	float n15_Mask2;
	float n15_Mask3;
	sgCustom_Countdown_33437(n13_Out, sg_Time, u_sgParams[0].x, n15_Mask1, n15_Mask2, n15_Mask3);
	// Multiply #23
	vec4 n23_Out = vec4_splat(n15_Mask1) * vec4(1.0, 0.692071199, 0.447988421, 1.0);
	// Fraction #17
	float n17_Out = fract(sg_Time);
	// Step #18
	float n18_Out = step(0.5, n17_Out);
	// Multiply #19
	float n19_Out = n18_Out * 0.25;
	// Add #20
	float n20_Out = 0.75 + n19_Out;
	// Multiply #21
	float n21_Out = n15_Mask2 * n20_Out;
	// Multiply #25
	vec4 n25_Out = vec4_splat(n21_Out) * vec4(1.0, 0.00719440775, 0.00232198136, 1.0);
	// Add #26
	vec4 n26_Out = n23_Out + n25_Out;
	// Multiply #28
	vec4 n28_Out = vec4_splat(n15_Mask3) * vec4(1.0, 0.170644939, 0.0100228256, 1.0);
	// Add #29
	vec4 n29_Out = n26_Out + n28_Out;
	// Add #31
	vec4 n31_Out = n29_Out + vec4(0.000928792579, 0.000116099072, 7.73993816e-05, 1.0);
	// Split #32
	vec2 n32_In = n13_Out;
	// Multiply #33
	float n33_Out = n32_In.y * 900.0;
	// Sine #34
	float n34_Out = sin(n33_Out);
	// Multiply #35
	float n35_Out = n34_Out * 0.119999997;
	// Add #36
	float n36_Out = 0.879999995 + n35_Out;
	// Subtract #37
	vec2 n37_Out = n13_Out - vec2(0.5, 0.5);
	// Length #38
	float n38_Out = length(n37_Out);
	// Remap #39
	float n39_Out = 1.0 + (n38_Out - 0.349999994) * (0.550000012 - 1.0) / (0.75 - 0.349999994);
	// Saturate #40
	float n40_Out = clamp(n39_Out, 0.0, 1.0);
	// Multiply #41
	float n41_Out = n36_Out * n40_Out;
	// Multiply #42
	vec4 n42_Out = n31_Out * vec4_splat(n41_Out);
	// Step #44
	float n44_Out = step(0.0, n32_In.x);
	// Step #45
	float n45_Out = step(n32_In.x, 1.0);
	// Multiply #46
	float n46_Out = n44_Out * n45_Out;
	// Step #47
	float n47_Out = step(0.0, n32_In.y);
	// Step #48
	float n48_Out = step(n32_In.y, 1.0);
	// Multiply #49
	float n49_Out = n47_Out * n48_Out;
	// Multiply #50
	float n50_Out = n46_Out * n49_Out;
	// Multiply #51
	float n51_Out = u_sgParams[1].x * n50_Out;
	// Multiply #52
	vec4 n52_Out = n42_Out * vec4_splat(n51_Out);
	// Outputs
	vec3 sgOut_BaseColor = vec3(0.00999999978, 0.00999999978, 0.0120000001);
	vec3 sgOut_Normal = vec3(0.0, 0.0, 1.0);
	float sgOut_Metallic = 0.0;
	float sgOut_Roughness = 0.300000012;
	vec3 sgOut_Emission = (n52_Out).xyz;
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
