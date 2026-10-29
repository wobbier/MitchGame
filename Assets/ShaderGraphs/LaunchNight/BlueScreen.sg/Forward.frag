$input v_worldPos, v_normal, v_tangent, v_bitangent, v_texcoord0, v_viewPos, v_objectPos, v_objectNormal

// Generated from Assets/ShaderGraphs/LaunchNight/BlueScreen.shadergraph by the shader graph compiler: edit the graph, not this file.

#include "Common.sh"
#include "StandardSurface.sh"
#include "ShaderGraph/SGLib.sh"
#include "Dither.sh"

uniform vec4 u_drawParams; // x screen-door fade (Dither.sh), per draw

uniform vec4 u_sgParams[16];
// u_sgParams[0]: Brightness (Float)
// u_sgParams[1]: UV Rect (Vector 4)
// u_sgParams[2]: Flip (Vector 2)

void sgCustom_Crash_83003(vec2 UV, out float Mask1, out float Mask2, out float Mask3)
{
Mask1 = 0.0;
Mask2 = 0.0;
Mask3 = 0.0;
{
    vec2 q = vec2((UV.x - 0.08) / 0.139286, (UV.y - 0.1) / 0.26);
    if (q.y >= 0.0 && q.y < 1.0 && q.x >= 0.0 && q.x < 2.0)
    {
        float ci = floor(q.x);
        float px = floor(fract(q.x) * 6.0);
        float py = floor(q.y * 7.0);
        float glo = 0.0;
        float ghi = 0.0;
        if (ci > -0.5 && ci < 0.5) { glo = 6336.0; ghi = 198.0; }
        if (ci > 0.5 && ci < 1.5) { glo = 67720.0; ghi = 8322.0; }
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
    vec2 q = vec2((UV.x - 0.08) / 0.026786, (UV.y - 0.46) / 0.05);
    if (q.y >= 0.0 && q.y < 1.0 && q.x >= 0.0 && q.x < 33.0)
    {
        float ci = floor(q.x);
        float px = floor(fract(q.x) * 6.0);
        float py = floor(q.y * 7.0);
        float glo = 0.0;
        float ghi = 0.0;
        if (ci > -0.5 && ci < 0.5) { glo = 141873.0; ghi = 4228.0; }
        if (ci > 0.5 && ci < 1.5) { glo = 575022.0; ghi = 14897.0; }
        if (ci > 1.5 && ci < 2.5) { glo = 575025.0; ghi = 14897.0; }
        if (ci > 2.5 && ci < 3.5) { glo = 509487.0; ghi = 17701.0; }
        if (ci > 4.5 && ci < 5.5) { glo = 509487.0; ghi = 15921.0; }
        if (ci > 5.5 && ci < 6.5) { glo = 575025.0; ghi = 14897.0; }
        if (ci > 6.5 && ci < 7.5) { glo = 135310.0; ghi = 14468.0; }
        if (ci > 7.5 && ci < 8.5) { glo = 33825.0; ghi = 31777.0; }
        if (ci > 8.5 && ci < 9.5) { glo = 575023.0; ghi = 15921.0; }
        if (ci > 10.5 && ci < 11.5) { glo = 509487.0; ghi = 17701.0; }
        if (ci > 11.5 && ci < 12.5) { glo = 1033774.0; ghi = 17969.0; }
        if (ci > 12.5 && ci < 13.5) { glo = 708145.0; ghi = 17977.0; }
        if (ci > 14.5 && ci < 15.5) { glo = 135310.0; ghi = 14468.0; }
        if (ci > 15.5 && ci < 16.5) { glo = 708145.0; ghi = 17977.0; }
        if (ci > 16.5 && ci < 17.5) { glo = 135327.0; ghi = 4228.0; }
        if (ci > 17.5 && ci < 18.5) { glo = 575022.0; ghi = 14897.0; }
        if (ci > 19.5 && ci < 20.5) { glo = 1033774.0; ghi = 17969.0; }
        if (ci > 21.5 && ci < 22.5) { glo = 509487.0; ghi = 1057.0; }
        if (ci > 22.5 && ci < 23.5) { glo = 509487.0; ghi = 17701.0; }
        if (ci > 23.5 && ci < 24.5) { glo = 575022.0; ghi = 14897.0; }
        if (ci > 24.5 && ci < 25.5) { glo = 509487.0; ghi = 15921.0; }
        if (ci > 25.5 && ci < 26.5) { glo = 33825.0; ghi = 31777.0; }
        if (ci > 26.5 && ci < 27.5) { glo = 492607.0; ghi = 31777.0; }
        if (ci > 27.5 && ci < 28.5) { glo = 710513.0; ghi = 17969.0; }
        if (ci > 29.5 && ci < 30.5) { glo = 1033774.0; ghi = 17969.0; }
        if (ci > 30.5 && ci < 31.5) { glo = 708145.0; ghi = 17977.0; }
        if (ci > 31.5 && ci < 32.5) { glo = 575023.0; ghi = 15921.0; }
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
    vec2 q = vec2((UV.x - 0.08) / 0.026786, (UV.y - 0.53) / 0.05);
    if (q.y >= 0.0 && q.y < 1.0 && q.x >= 0.0 && q.x < 28.0)
    {
        float ci = floor(q.x);
        float px = floor(fract(q.x) * 6.0);
        float py = floor(q.y * 7.0);
        float glo = 0.0;
        float ghi = 0.0;
        if (ci > -0.5 && ci < 0.5) { glo = 708145.0; ghi = 17977.0; }
        if (ci > 0.5 && ci < 1.5) { glo = 492607.0; ghi = 31777.0; }
        if (ci > 1.5 && ci < 2.5) { glo = 492607.0; ghi = 31777.0; }
        if (ci > 2.5 && ci < 3.5) { glo = 575023.0; ghi = 15921.0; }
        if (ci > 3.5 && ci < 4.5) { glo = 459838.0; ghi = 15888.0; }
        if (ci > 5.5 && ci < 6.5) { glo = 135327.0; ghi = 4228.0; }
        if (ci > 6.5 && ci < 7.5) { glo = 575022.0; ghi = 14897.0; }
        if (ci > 8.5 && ci < 9.5) { glo = 509487.0; ghi = 17701.0; }
        if (ci > 9.5 && ci < 10.5) { glo = 492607.0; ghi = 31777.0; }
        if (ci > 10.5 && ci < 11.5) { glo = 459838.0; ghi = 15888.0; }
        if (ci > 11.5 && ci < 12.5) { glo = 135327.0; ghi = 4228.0; }
        if (ci > 12.5 && ci < 13.5) { glo = 1033774.0; ghi = 17969.0; }
        if (ci > 13.5 && ci < 14.5) { glo = 509487.0; ghi = 17701.0; }
        if (ci > 14.5 && ci < 15.5) { glo = 135327.0; ghi = 4228.0; }
        if (ci > 15.5 && ci < 16.5) { glo = 0.0; ghi = 6336.0; }
        if (ci > 17.5 && ci < 18.5) { glo = 706097.0; ghi = 10933.0; }
        if (ci > 18.5 && ci < 19.5) { glo = 492607.0; ghi = 31777.0; }
        if (ci > 19.5 && ci < 20.5) { glo = 2180.0; ghi = 0.0; }
        if (ci > 20.5 && ci < 21.5) { glo = 509487.0; ghi = 17701.0; }
        if (ci > 21.5 && ci < 22.5) { glo = 492607.0; ghi = 31777.0; }
        if (ci > 23.5 && ci < 24.5) { glo = 270620.0; ghi = 6440.0; }
        if (ci > 24.5 && ci < 25.5) { glo = 575025.0; ghi = 14897.0; }
        if (ci > 25.5 && ci < 26.5) { glo = 459838.0; ghi = 15888.0; }
        if (ci > 26.5 && ci < 27.5) { glo = 135327.0; ghi = 4228.0; }
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
    vec2 q = vec2((UV.x - 0.08) / 0.026786, (UV.y - 0.6) / 0.05);
    if (q.y >= 0.0 && q.y < 1.0 && q.x >= 0.0 && q.x < 27.0)
    {
        float ci = floor(q.x);
        float px = floor(fract(q.x) * 6.0);
        float py = floor(q.y * 7.0);
        float glo = 0.0;
        float ghi = 0.0;
        if (ci > -0.5 && ci < 0.5) { glo = 34350.0; ghi = 14881.0; }
        if (ci > 0.5 && ci < 1.5) { glo = 575022.0; ghi = 14897.0; }
        if (ci > 1.5 && ci < 2.5) { glo = 33825.0; ghi = 31777.0; }
        if (ci > 2.5 && ci < 3.5) { glo = 33825.0; ghi = 31777.0; }
        if (ci > 3.5 && ci < 4.5) { glo = 492607.0; ghi = 31777.0; }
        if (ci > 4.5 && ci < 5.5) { glo = 34350.0; ghi = 14881.0; }
        if (ci > 5.5 && ci < 6.5) { glo = 135327.0; ghi = 4228.0; }
        if (ci > 6.5 && ci < 7.5) { glo = 135310.0; ghi = 14468.0; }
        if (ci > 7.5 && ci < 8.5) { glo = 708145.0; ghi = 17977.0; }
        if (ci > 8.5 && ci < 9.5) { glo = 951854.0; ghi = 31281.0; }
        if (ci > 10.5 && ci < 11.5) { glo = 459838.0; ghi = 15888.0; }
        if (ci > 11.5 && ci < 12.5) { glo = 575022.0; ghi = 14897.0; }
        if (ci > 12.5 && ci < 13.5) { glo = 710513.0; ghi = 17969.0; }
        if (ci > 13.5 && ci < 14.5) { glo = 492607.0; ghi = 31777.0; }
        if (ci > 15.5 && ci < 16.5) { glo = 492607.0; ghi = 31777.0; }
        if (ci > 16.5 && ci < 17.5) { glo = 509487.0; ghi = 17701.0; }
        if (ci > 17.5 && ci < 18.5) { glo = 509487.0; ghi = 17701.0; }
        if (ci > 18.5 && ci < 19.5) { glo = 575022.0; ghi = 14897.0; }
        if (ci > 19.5 && ci < 20.5) { glo = 509487.0; ghi = 17701.0; }
        if (ci > 21.5 && ci < 22.5) { glo = 135310.0; ghi = 14468.0; }
        if (ci > 22.5 && ci < 23.5) { glo = 708145.0; ghi = 17977.0; }
        if (ci > 23.5 && ci < 24.5) { glo = 492607.0; ghi = 1057.0; }
        if (ci > 24.5 && ci < 25.5) { glo = 575022.0; ghi = 14897.0; }
        if (ci > 25.5 && ci < 26.5) { glo = 0.0; ghi = 6336.0; }
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
    vec2 q = vec2((UV.x - 0.08) / 0.026786, (UV.y - 0.7) / 0.05);
    if (q.y >= 0.0 && q.y < 1.0 && q.x >= 0.0 && q.x < 11.0)
    {
        float ci = floor(q.x);
        float px = floor(fract(q.x) * 6.0);
        float py = floor(q.y * 7.0);
        float glo = 0.0;
        float ghi = 0.0;
        if (ci > -0.5 && ci < 0.5) { glo = 305544.0; ghi = 8479.0; }
        if (ci > 0.5 && ci < 1.5) { glo = 139891.0; ghi = 26402.0; }
        if (ci > 2.5 && ci < 3.5) { glo = 34350.0; ghi = 14881.0; }
        if (ci > 3.5 && ci < 4.5) { glo = 575022.0; ghi = 14897.0; }
        if (ci > 4.5 && ci < 5.5) { glo = 710513.0; ghi = 17969.0; }
        if (ci > 5.5 && ci < 6.5) { glo = 509487.0; ghi = 1057.0; }
        if (ci > 6.5 && ci < 7.5) { glo = 33825.0; ghi = 31777.0; }
        if (ci > 7.5 && ci < 8.5) { glo = 492607.0; ghi = 31777.0; }
        if (ci > 8.5 && ci < 9.5) { glo = 135327.0; ghi = 4228.0; }
        if (ci > 9.5 && ci < 10.5) { glo = 492607.0; ghi = 31777.0; }
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
    vec2 q = vec2((UV.x - 0.08) / 0.021429, (UV.y - 0.84) / 0.04);
    if (q.y >= 0.0 && q.y < 1.0 && q.x >= 0.0 && q.x < 25.0)
    {
        float ci = floor(q.x);
        float px = floor(fract(q.x) * 6.0);
        float py = floor(q.y * 7.0);
        float glo = 0.0;
        float ghi = 0.0;
        if (ci > -0.5 && ci < 0.5) { glo = 459838.0; ghi = 15888.0; }
        if (ci > 0.5 && ci < 1.5) { glo = 135327.0; ghi = 4228.0; }
        if (ci > 1.5 && ci < 2.5) { glo = 575022.0; ghi = 14897.0; }
        if (ci > 2.5 && ci < 3.5) { glo = 509487.0; ghi = 1057.0; }
        if (ci > 4.5 && ci < 5.5) { glo = 34350.0; ghi = 14881.0; }
        if (ci > 5.5 && ci < 6.5) { glo = 575022.0; ghi = 14897.0; }
        if (ci > 6.5 && ci < 7.5) { glo = 575023.0; ghi = 15921.0; }
        if (ci > 7.5 && ci < 8.5) { glo = 492607.0; ghi = 31777.0; }
        if (ci > 8.5 && ci < 9.5) { glo = 6336.0; ghi = 198.0; }
        if (ci > 10.5 && ci < 11.5) { glo = 459838.0; ghi = 15888.0; }
        if (ci > 11.5 && ci < 12.5) { glo = 1033777.0; ghi = 17969.0; }
        if (ci > 12.5 && ci < 13.5) { glo = 135310.0; ghi = 14468.0; }
        if (ci > 13.5 && ci < 14.5) { glo = 509487.0; ghi = 1057.0; }
        if (ci > 14.5 && ci < 15.5) { glo = 0.0; ghi = 31744.0; }
        if (ci > 15.5 && ci < 16.5) { glo = 135310.0; ghi = 14468.0; }
        if (ci > 16.5 && ci < 17.5) { glo = 135327.0; ghi = 4228.0; }
        if (ci > 17.5 && ci < 18.5) { glo = 0.0; ghi = 31744.0; }
        if (ci > 18.5 && ci < 19.5) { glo = 1033774.0; ghi = 17969.0; }
        if (ci > 19.5 && ci < 20.5) { glo = 708145.0; ghi = 17977.0; }
        if (ci > 20.5 && ci < 21.5) { glo = 141873.0; ghi = 4228.0; }
        if (ci > 21.5 && ci < 22.5) { glo = 706097.0; ghi = 10933.0; }
        if (ci > 22.5 && ci < 23.5) { glo = 1033774.0; ghi = 17969.0; }
        if (ci > 23.5 && ci < 24.5) { glo = 141873.0; ghi = 4228.0; }
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
	if (ditherDrops(u_drawParams.x, gl_FragCoord.xy))
	{
		discard;
	}
	vec4 sg_fragCoord = gl_FragCoord;
	bool sg_frontFacing = gl_FrontFacing;
	vec2 sg_UV0 = v_texcoord0;

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
	// Crash #13
	float n13_Mask1;
	float n13_Mask2;
	float n13_Mask3;
	sgCustom_Crash_83003(n12_Out, n13_Mask1, n13_Mask2, n13_Mask3);
	// Multiply #15
	vec4 n15_Out = vec4_splat(n13_Mask1) * vec4(1.0, 1.0, 1.0, 1.0);
	// Add #17
	vec4 n17_Out = n15_Out + vec4(0.0, 0.0396819152, 0.34239164, 1.0);
	// Split #18
	vec2 n18_In = n12_Out;
	// Multiply #19
	float n19_Out = n18_In.y * 900.0;
	// Sine #20
	float n20_Out = sin(n19_Out);
	// Multiply #21
	float n21_Out = n20_Out * 0.119999997;
	// Add #22
	float n22_Out = 0.879999995 + n21_Out;
	// Subtract #23
	vec2 n23_Out = n12_Out - vec2(0.5, 0.5);
	// Length #24
	float n24_Out = length(n23_Out);
	// Remap #25
	float n25_Out = 1.0 + (n24_Out - 0.349999994) * (0.550000012 - 1.0) / (0.75 - 0.349999994);
	// Saturate #26
	float n26_Out = clamp(n25_Out, 0.0, 1.0);
	// Multiply #27
	float n27_Out = n22_Out * n26_Out;
	// Multiply #28
	vec4 n28_Out = n17_Out * vec4_splat(n27_Out);
	// Step #30
	float n30_Out = step(0.0, n18_In.x);
	// Step #31
	float n31_Out = step(n18_In.x, 1.0);
	// Multiply #32
	float n32_Out = n30_Out * n31_Out;
	// Step #33
	float n33_Out = step(0.0, n18_In.y);
	// Step #34
	float n34_Out = step(n18_In.y, 1.0);
	// Multiply #35
	float n35_Out = n33_Out * n34_Out;
	// Multiply #36
	float n36_Out = n32_Out * n35_Out;
	// Multiply #37
	float n37_Out = u_sgParams[0].x * n36_Out;
	// Multiply #38
	vec4 n38_Out = n28_Out * vec4_splat(n37_Out);
	// Outputs
	vec3 sgOut_BaseColor = vec3(0.00999999978, 0.00999999978, 0.0120000001);
	vec3 sgOut_Normal = vec3(0.0, 0.0, 1.0);
	float sgOut_Metallic = 0.0;
	float sgOut_Roughness = 0.300000012;
	vec3 sgOut_Emission = (n38_Out).xyz;
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
