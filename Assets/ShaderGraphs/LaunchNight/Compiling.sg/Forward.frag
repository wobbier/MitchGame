$input v_worldPos, v_normal, v_tangent, v_bitangent, v_texcoord0, v_viewPos, v_objectPos, v_objectNormal

// Generated from Assets/ShaderGraphs/LaunchNight/Compiling.shadergraph by the shader graph compiler: edit the graph, not this file.

#include "Common.sh"
#include "StandardSurface.sh"
#include "ShaderGraph/SGLib.sh"
#include "Dither.sh"

uniform vec4 u_drawParams; // x screen-door fade (Dither.sh), per draw

uniform vec4 u_sgParams[16];
// u_sgParams[0]: Brightness (Float)
// u_sgParams[1]: UV Rect (Vector 4)
// u_sgParams[2]: Flip (Vector 2)

void sgCustom_Compile_38731(vec2 UV, out float Mask1, out float Mask2, out float Mask3)
{
Mask1 = 0.0;
Mask2 = 0.0;
Mask3 = 0.0;
{
    vec2 q = vec2((UV.x - 0.06) / 0.032143, (UV.y - 0.1) / 0.06);
    if (q.y >= 0.0 && q.y < 1.0 && q.x >= 0.0 && q.x < 17.0)
    {
        float ci = floor(q.x);
        float px = floor(fract(q.x) * 6.0);
        float py = floor(q.y * 7.0);
        float glo = 0.0;
        float ghi = 0.0;
        if (ci > -0.5 && ci < 0.5) { glo = 532610.0; ghi = 2184.0; }
        if (ci > 1.5 && ci < 2.5) { glo = 509487.0; ghi = 15921.0; }
        if (ci > 2.5 && ci < 3.5) { glo = 575025.0; ghi = 14897.0; }
        if (ci > 3.5 && ci < 4.5) { glo = 135310.0; ghi = 14468.0; }
        if (ci > 4.5 && ci < 5.5) { glo = 33825.0; ghi = 31777.0; }
        if (ci > 5.5 && ci < 6.5) { glo = 575023.0; ghi = 15921.0; }
        if (ci > 6.5 && ci < 7.5) { glo = 0.0; ghi = 6336.0; }
        if (ci > 7.5 && ci < 8.5) { glo = 459838.0; ghi = 15888.0; }
        if (ci > 8.5 && ci < 9.5) { glo = 1033777.0; ghi = 17969.0; }
        if (ci > 10.5 && ci < 11.5) { glo = 1015808.0; ghi = 0.0; }
        if (ci > 11.5 && ci < 12.5) { glo = 1015808.0; ghi = 0.0; }
        if (ci > 12.5 && ci < 13.5) { glo = 459838.0; ghi = 15888.0; }
        if (ci > 13.5 && ci < 14.5) { glo = 1033777.0; ghi = 17969.0; }
        if (ci > 14.5 && ci < 15.5) { glo = 135310.0; ghi = 14468.0; }
        if (ci > 15.5 && ci < 16.5) { glo = 509487.0; ghi = 1057.0; }
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
    vec2 q = vec2((UV.x - 0.06) / 0.0375, (UV.y - 0.24) / 0.07);
    if (q.y >= 0.0 && q.y < 1.0 && q.x >= 0.0 && q.x < 17.0)
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
        if (ci > 5.5 && ci < 6.5) { glo = 135310.0; ghi = 14468.0; }
        if (ci > 6.5 && ci < 7.5) { glo = 708145.0; ghi = 17977.0; }
        if (ci > 7.5 && ci < 8.5) { glo = 951854.0; ghi = 31281.0; }
        if (ci > 9.5 && ci < 10.5) { glo = 459838.0; ghi = 15888.0; }
        if (ci > 10.5 && ci < 11.5) { glo = 1033777.0; ghi = 17969.0; }
        if (ci > 11.5 && ci < 12.5) { glo = 1033774.0; ghi = 17969.0; }
        if (ci > 12.5 && ci < 13.5) { glo = 575023.0; ghi = 15921.0; }
        if (ci > 13.5 && ci < 14.5) { glo = 492607.0; ghi = 31777.0; }
        if (ci > 14.5 && ci < 15.5) { glo = 509487.0; ghi = 17701.0; }
        if (ci > 15.5 && ci < 16.5) { glo = 459838.0; ghi = 15888.0; }
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
    vec2 q = vec2((UV.x - 0.06) / 0.0375, (UV.y - 0.36) / 0.07);
    if (q.y >= 0.0 && q.y < 1.0 && q.x >= 0.0 && q.x < 13.0)
    {
        float ci = floor(q.x);
        float px = floor(fract(q.x) * 6.0);
        float py = floor(q.y * 7.0);
        float glo = 0.0;
        float ghi = 0.0;
        if (ci > -0.5 && ci < 0.5) { glo = 305544.0; ghi = 8479.0; }
        if (ci > 0.5 && ci < 1.5) { glo = 139807.0; ghi = 2114.0; }
        if (ci > 1.5 && ci < 2.5) { glo = 266527.0; ghi = 14896.0; }
        if (ci > 2.5 && ci < 3.5) { glo = 1001006.0; ghi = 6416.0; }
        if (ci > 3.5 && ci < 4.5) { glo = 135364.0; ghi = 14468.0; }
        if (ci > 5.5 && ci < 6.5) { glo = 139536.0; ghi = 1090.0; }
        if (ci > 7.5 && ci < 8.5) { glo = 305544.0; ghi = 8479.0; }
        if (ci > 8.5 && ci < 9.5) { glo = 139807.0; ghi = 2114.0; }
        if (ci > 9.5 && ci < 10.5) { glo = 266527.0; ghi = 14896.0; }
        if (ci > 10.5 && ci < 11.5) { glo = 1001006.0; ghi = 6416.0; }
        if (ci > 11.5 && ci < 12.5) { glo = 279086.0; ghi = 31812.0; }
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
    vec2 q = vec2((UV.x - 0.06) / 0.042857, (UV.y - 0.52) / 0.08);
    if (q.y >= 0.0 && q.y < 1.0 && q.x >= 0.0 && q.x < 1.0)
    {
        float ci = floor(q.x);
        float px = floor(fract(q.x) * 6.0);
        float py = floor(q.y * 7.0);
        float glo = 0.0;
        float ghi = 0.0;
        if (ci > -0.5 && ci < 0.5) { glo = 67662.0; ghi = 14402.0; }
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
    vec2 q = vec2((UV.x - 0.85) / 0.042857, (UV.y - 0.52) / 0.08);
    if (q.y >= 0.0 && q.y < 1.0 && q.x >= 0.0 && q.x < 1.0)
    {
        float ci = floor(q.x);
        float px = floor(fract(q.x) * 6.0);
        float py = floor(q.y * 7.0);
        float glo = 0.0;
        float ghi = 0.0;
        if (ci > -0.5 && ci < 0.5) { glo = 270606.0; ghi = 14600.0; }
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
    vec2 q = vec2((UV.x - 0.06) / 0.042857, (UV.y - 0.66) / 0.08);
    if (q.y >= 0.0 && q.y < 1.0 && q.x >= 0.0 && q.x < 3.0)
    {
        float ci = floor(q.x);
        float px = floor(fract(q.x) * 6.0);
        float py = floor(q.y * 7.0);
        float glo = 0.0;
        float ghi = 0.0;
        if (ci > -0.5 && ci < 0.5) { glo = 1001006.0; ghi = 6416.0; }
        if (ci > 0.5 && ci < 1.5) { glo = 1001006.0; ghi = 6416.0; }
        if (ci > 1.5 && ci < 2.5) { glo = 139891.0; ghi = 26402.0; }
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
    vec2 q = vec2((UV.x - 0.06) / 0.032143, (UV.y - 0.82) / 0.06);
    if (q.y >= 0.0 && q.y < 1.0 && q.x >= 0.0 && q.x < 14.0)
    {
        float ci = floor(q.x);
        float px = floor(fract(q.x) * 6.0);
        float py = floor(q.y * 7.0);
        float glo = 0.0;
        float ghi = 0.0;
        if (ci > -0.5 && ci < 0.5) { glo = 492607.0; ghi = 31777.0; }
        if (ci > 0.5 && ci < 1.5) { glo = 135327.0; ghi = 4228.0; }
        if (ci > 1.5 && ci < 2.5) { glo = 1033774.0; ghi = 17969.0; }
        if (ci > 2.5 && ci < 3.5) { glo = 6336.0; ghi = 198.0; }
        if (ci > 4.5 && ci < 5.5) { glo = 266527.0; ghi = 14896.0; }
        if (ci > 6.5 && ci < 7.5) { glo = 710513.0; ghi = 17969.0; }
        if (ci > 7.5 && ci < 8.5) { glo = 135310.0; ghi = 14468.0; }
        if (ci > 8.5 && ci < 9.5) { glo = 708145.0; ghi = 17977.0; }
        if (ci > 9.5 && ci < 10.5) { glo = 575025.0; ghi = 14897.0; }
        if (ci > 10.5 && ci < 11.5) { glo = 135327.0; ghi = 4228.0; }
        if (ci > 11.5 && ci < 12.5) { glo = 492607.0; ghi = 31777.0; }
        if (ci > 12.5 && ci < 13.5) { glo = 459838.0; ghi = 15888.0; }
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
	if (ditherDrops(u_drawParams.x, gl_FragCoord.xy))
	{
		discard;
	}
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
	// Compile #13
	float n13_Mask1;
	float n13_Mask2;
	float n13_Mask3;
	sgCustom_Compile_38731(n12_Out, n13_Mask1, n13_Mask2, n13_Mask3);
	// Split #14
	vec2 n14_In = n12_Out;
	// Step #20
	float n20_Out = step(0.100000001, n14_In.x);
	// Multiply #16
	float n16_Out = sg_Time * 0.310000002;
	// Sine #17
	float n17_Out = sin(n16_Out);
	// Multiply #18
	float n18_Out = n17_Out * 0.00300000003;
	// Add #19
	float n19_Out = 0.839999974 + n18_Out;
	// Step #21
	float n21_Out = step(n14_In.x, n19_Out);
	// Multiply #22
	float n22_Out = n20_Out * n21_Out;
	// Step #23
	float n23_Out = step(0.535000026, n14_In.y);
	// Step #24
	float n24_Out = step(n14_In.y, 0.584999979);
	// Multiply #25
	float n25_Out = n23_Out * n24_Out;
	// Multiply #26
	float n26_Out = n22_Out * n25_Out;
	// Add #30
	float n30_Out = n13_Mask1 + n26_Out;
	// Multiply #33
	vec4 n33_Out = vec4_splat(n30_Out) * vec4(0.0508760884, 1.0, 0.132868335, 1.0);
	// Multiply #27
	float n27_Out = sg_Time * 1.29999995;
	// Fraction #28
	float n28_Out = fract(n27_Out);
	// Step #29
	float n29_Out = step(0.5, n28_Out);
	// Multiply #31
	float n31_Out = n13_Mask3 * n29_Out;
	// Multiply #35
	vec4 n35_Out = vec4_splat(n31_Out) * vec4(0.603827417, 1.0, 0.692071199, 1.0);
	// Add #36
	vec4 n36_Out = n33_Out + n35_Out;
	// Add #38
	vec4 n38_Out = n36_Out + vec4(0.0, 0.00154798757, 0.0, 1.0);
	// Multiply #40
	float n40_Out = n14_In.y * 900.0;
	// Sine #41
	float n41_Out = sin(n40_Out);
	// Multiply #42
	float n42_Out = n41_Out * 0.119999997;
	// Add #43
	float n43_Out = 0.879999995 + n42_Out;
	// Subtract #44
	vec2 n44_Out = n12_Out - vec2(0.5, 0.5);
	// Length #45
	float n45_Out = length(n44_Out);
	// Remap #46
	float n46_Out = 1.0 + (n45_Out - 0.349999994) * (0.550000012 - 1.0) / (0.75 - 0.349999994);
	// Saturate #47
	float n47_Out = clamp(n46_Out, 0.0, 1.0);
	// Multiply #48
	float n48_Out = n43_Out * n47_Out;
	// Multiply #49
	vec4 n49_Out = n38_Out * vec4_splat(n48_Out);
	// Step #51
	float n51_Out = step(0.0, n14_In.x);
	// Step #52
	float n52_Out = step(n14_In.x, 1.0);
	// Multiply #53
	float n53_Out = n51_Out * n52_Out;
	// Step #54
	float n54_Out = step(0.0, n14_In.y);
	// Step #55
	float n55_Out = step(n14_In.y, 1.0);
	// Multiply #56
	float n56_Out = n54_Out * n55_Out;
	// Multiply #57
	float n57_Out = n53_Out * n56_Out;
	// Multiply #58
	float n58_Out = u_sgParams[0].x * n57_Out;
	// Multiply #59
	vec4 n59_Out = n49_Out * vec4_splat(n58_Out);
	// Outputs
	vec3 sgOut_BaseColor = vec3(0.00999999978, 0.00999999978, 0.0120000001);
	vec3 sgOut_Normal = vec3(0.0, 0.0, 1.0);
	float sgOut_Metallic = 0.0;
	float sgOut_Roughness = 0.300000012;
	vec3 sgOut_Emission = (n59_Out).xyz;
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
