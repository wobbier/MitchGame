$input v_worldPos, v_normal, v_tangent, v_bitangent, v_texcoord0, v_viewPos, v_objectPos, v_objectNormal

// Generated from Assets/ShaderGraphs/LostTemple/AncientStone.shadergraph by the shader graph compiler: edit the graph, not this file.

#include "Common.sh"
#include "StandardSurface.sh"
#include "ShaderGraph/SGLib.sh"
#include "Dither.sh"

uniform vec4 u_drawParams; // x screen-door fade (Dither.sh), per draw

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
	if (ditherDrops(u_drawParams.x, gl_FragCoord.xy))
	{
		discard;
	}
	vec4 sg_fragCoord = gl_FragCoord;
	bool sg_frontFacing = gl_FrontFacing;
	vec3 sg_PositionWorld = v_worldPos;
	vec3 sg_NormalWorld = sgSafeNormalize(v_normal);
	vec3 sg_TangentWorld = sgSafeNormalize(v_tangent);
	vec3 sg_BitangentWorld = sgSafeNormalize(v_bitangent);

	// Triplanar #16
	vec4 n16_Out = toLinear(sgTriplanar(s_sgTex0, sg_PositionWorld, sg_NormalWorld, u_sgParams[3].x, 6.0));
	// Swizzle .xyz #17
	vec3 n17_Out = (n16_Out).xyz;
	// Multiply #25
	vec3 n25_Out = n17_Out * u_sgParams[0].xyz;
	// Multiply #20
	float n20_Out = u_sgParams[9].x * 0.5;
	// Subtract #21
	float n21_Out = 1.0 - n20_Out;
	// Masonry #18
	float n18_Mortar;
	float n18_Bevel;
	float n18_Block;
	sgCustom_Masonry_17942(sg_PositionWorld, sg_NormalWorld, u_sgParams[7].xy, 0.0299999993, u_sgParams[8].x, n18_Mortar, n18_Bevel, n18_Block);
	// Multiply #22
	float n22_Out = n18_Block * u_sgParams[9].x;
	// Add #23
	float n23_Out = n21_Out + n22_Out;
	// Lerp #24
	float n24_Out = mix(1.0, n23_Out, u_sgParams[6].x);
	// Multiply #19
	float n19_Out = n18_Mortar * u_sgParams[6].x;
	// Lerp #26
	float n26_Out = mix(1.0, 0.349999994, n19_Out);
	// Multiply #27
	float n27_Out = n24_Out * n26_Out;
	// Multiply #28
	vec3 n28_Out = n25_Out * vec3_splat(n27_Out);
	// Multiply #34
	float n34_Out = u_sgParams[3].x * 2.29999995;
	// Triplanar #35
	vec4 n35_Out = toLinear(sgTriplanar(s_sgTex1, sg_PositionWorld, sg_NormalWorld, n34_Out, 4.0));
	// Swizzle .xyz #36
	vec3 n36_Out = (n35_Out).xyz;
	// Multiply #37
	vec3 n37_Out = n36_Out * u_sgParams[1].xyz;
	// Subtract #46
	float n46_Out = 1.14999998 - u_sgParams[2].x;
	// Add #47
	float n47_Out = n46_Out + 0.200000003;
	// Split #38
	vec3 n38_In = sg_NormalWorld;
	// Multiply #41
	float n41_Out = n38_In.y * 0.699999988;
	// Swizzle .xz #39
	vec2 n39_Out = (vec4(sg_PositionWorld, 1.0)).xz;
	// Fractal Noise #40
	float n40_Out = sgFractalNoise(n39_Out, 0.600000024, 4.0, 2.0, 0.5);
	// Multiply #42
	float n42_Out = n40_Out * 0.600000024;
	// Add #43
	float n43_Out = n41_Out + n42_Out;
	// Multiply #44
	float n44_Out = n19_Out * 0.349999994;
	// Add #45
	float n45_Out = n43_Out + n44_Out;
	// Smoothstep #48
	float n48_Out = smoothstep(n46_Out, n47_Out, n45_Out);
	// Lerp #53
	vec3 n53_Out = mix(n28_Out, n37_Out, vec3_splat(n48_Out));
	// Split #49
	vec3 n49_In = sg_PositionWorld;
	// Subtract #50
	float n50_Out = n49_In.y - u_sgParams[4].x;
	// Smoothstep #51
	float n51_Out = smoothstep(0.0, 0.800000012, n50_Out);
	// One Minus #52
	float n52_Out = 1.0 - n51_Out;
	// Lerp #54
	float n54_Out = mix(1.0, 0.449999988, n52_Out);
	// Multiply #55
	vec3 n55_Out = n53_Out * vec3_splat(n54_Out);
	// Luminance #29
	float n29_Out = sgLuminance(n17_Out);
	// Multiply #30
	float n30_Out = n29_Out * 0.5;
	// Lerp #31
	float n31_Out = mix(0.5, n18_Bevel, u_sgParams[6].x);
	// Multiply #32
	float n32_Out = n31_Out * 0.5;
	// Add #33
	float n33_Out = n30_Out + n32_Out;
	// Normal From Height #59
	vec3 n59_Out = sgWorldToTangent(sgNormalFromHeight(n33_Out, 0.600000024, sg_PositionWorld, sg_NormalWorld), sg_TangentWorld, sg_BitangentWorld, sg_NormalWorld);
	// Maximum #56
	float n56_Out = max(n48_Out, n19_Out);
	// Lerp #57
	float n57_Out = mix(u_sgParams[5].x, 0.949999988, n56_Out);
	// Lerp #58
	float n58_Out = mix(n57_Out, 0.180000007, n52_Out);
	// Remap #60
	float n60_Out = 0.550000012 + (n33_Out - 0.0500000007) * (1.0 - 0.550000012) / (0.5 - 0.0500000007);
	// Saturate #61
	float n61_Out = clamp(n60_Out, 0.0, 1.0);
	// Lerp #62
	float n62_Out = mix(1.0, 0.449999988, n19_Out);
	// Multiply #63
	float n63_Out = n61_Out * n62_Out;
	// Outputs
	vec3 sgOut_BaseColor = n55_Out;
	vec3 sgOut_Normal = n59_Out;
	float sgOut_Metallic = 0.0;
	float sgOut_Roughness = n58_Out;
	vec3 sgOut_Emission = vec3(0.0, 0.0, 0.0);
	float sgOut_Occlusion = n63_Out;
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
