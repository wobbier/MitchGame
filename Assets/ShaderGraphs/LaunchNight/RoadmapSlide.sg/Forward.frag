$input v_worldPos, v_normal, v_tangent, v_bitangent, v_texcoord0, v_viewPos, v_objectPos, v_objectNormal

// Generated from Assets/ShaderGraphs/LaunchNight/RoadmapSlide.shadergraph by the shader graph compiler: edit the graph, not this file.

#include "Common.sh"
#include "StandardSurface.sh"
#include "ShaderGraph/SGLib.sh"
#include "Dither.sh"

uniform vec4 u_drawParams; // x screen-door fade (Dither.sh), per draw

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
	// Split #15
	vec2 n15_In = n12_Out;
	// Step #16
	float n16_Out = step(n15_In.y, 0.209999993);
	// Step #17
	float n17_Out = step(0.200000003, n15_In.y);
	// Multiply #18
	float n18_Out = n16_Out * n17_Out;
	// Multiply #38
	float n38_Out = n18_Out * 0.0;
	// Lerp #39
	vec4 n39_Out = mix(vec4(0.827570975, 0.848088384, 0.890005529, 1.0), vec4(0.0100228256, 0.0508760884, 0.318546832, 1.0), vec4_splat(n38_Out));
	// Slide #13
	float n13_Mask1;
	float n13_Mask2;
	float n13_Mask3;
	sgCustom_Slide_8256(n12_Out, n13_Mask1, n13_Mask2, n13_Mask3);
	// Add #31
	float n31_Out = n13_Mask1 + n13_Mask2;
	// Chart #14
	float n14_Axes;
	float n14_Curve;
	float n14_Here;
	sgCustom_Chart_75953(n12_Out, n14_Axes, n14_Curve, n14_Here);
	// Add #32
	float n32_Out = n13_Mask3 + n14_Axes;
	// Add #33
	float n33_Out = n14_Curve + n14_Here;
	// Add #34
	float n34_Out = n32_Out + n33_Out;
	// Add #35
	float n35_Out = n31_Out + n34_Out;
	// Saturate #36
	float n36_Out = clamp(n35_Out, 0.0, 1.0);
	// One Minus #40
	float n40_Out = 1.0 - n36_Out;
	// Multiply #41
	vec4 n41_Out = n39_Out * vec4_splat(n40_Out);
	// Add #20
	float n20_Out = n13_Mask1 + n14_Axes;
	// Multiply #22
	vec4 n22_Out = vec4_splat(n20_Out) * vec4(0.0100228256, 0.0219809469, 0.106539242, 1.0);
	// Maximum #24
	float n24_Out = max(n13_Mask2, n33_Out);
	// Multiply #26
	vec4 n26_Out = vec4_splat(n24_Out) * vec4(0.787412345, 0.0134117464, 0.0100228256, 1.0);
	// Add #27
	vec4 n27_Out = n22_Out + n26_Out;
	// Multiply #29
	vec4 n29_Out = vec4_splat(n13_Mask3) * vec4(0.263273418, 0.263273418, 0.318546832, 1.0);
	// Add #30
	vec4 n30_Out = n27_Out + n29_Out;
	// Add #42
	vec4 n42_Out = n41_Out + n30_Out;
	// Multiply #44
	vec4 n44_Out = vec4_splat(n18_Out) * vec4(0.0, 0.0508760884, 0.380056322, 1.0);
	// Add #45
	vec4 n45_Out = n42_Out + n44_Out;
	// Multiply #47
	float n47_Out = n15_In.y * 900.0;
	// Sine #48
	float n48_Out = sin(n47_Out);
	// Multiply #49
	float n49_Out = n48_Out * 0.119999997;
	// Add #50
	float n50_Out = 0.879999995 + n49_Out;
	// Subtract #51
	vec2 n51_Out = n12_Out - vec2(0.5, 0.5);
	// Length #52
	float n52_Out = length(n51_Out);
	// Remap #53
	float n53_Out = 1.0 + (n52_Out - 0.349999994) * (0.550000012 - 1.0) / (0.75 - 0.349999994);
	// Saturate #54
	float n54_Out = clamp(n53_Out, 0.0, 1.0);
	// Multiply #55
	float n55_Out = n50_Out * n54_Out;
	// Multiply #56
	vec4 n56_Out = n45_Out * vec4_splat(n55_Out);
	// Step #58
	float n58_Out = step(0.0, n15_In.x);
	// Step #59
	float n59_Out = step(n15_In.x, 1.0);
	// Multiply #60
	float n60_Out = n58_Out * n59_Out;
	// Step #61
	float n61_Out = step(0.0, n15_In.y);
	// Step #62
	float n62_Out = step(n15_In.y, 1.0);
	// Multiply #63
	float n63_Out = n61_Out * n62_Out;
	// Multiply #64
	float n64_Out = n60_Out * n63_Out;
	// Multiply #65
	float n65_Out = u_sgParams[0].x * n64_Out;
	// Multiply #66
	vec4 n66_Out = n56_Out * vec4_splat(n65_Out);
	// Outputs
	vec3 sgOut_BaseColor = vec3(0.00999999978, 0.00999999978, 0.0120000001);
	vec3 sgOut_Normal = vec3(0.0, 0.0, 1.0);
	float sgOut_Metallic = 0.0;
	float sgOut_Roughness = 0.300000012;
	vec3 sgOut_Emission = (n66_Out).xyz;
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
