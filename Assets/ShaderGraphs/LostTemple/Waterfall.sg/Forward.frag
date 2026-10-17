$input v_worldPos, v_normal, v_tangent, v_bitangent, v_texcoord0, v_viewPos, v_objectPos, v_objectNormal

// Generated from Assets/ShaderGraphs/LostTemple/Waterfall.shadergraph by the shader graph compiler: edit the graph, not this file.
#define SG_TRANSPARENT 1

#include "Common.sh"
#include "StandardSurface.sh"
#include "ShaderGraph/SGLib.sh"

uniform vec4 u_sgParams[16];
// u_sgParams[0]: Water Color (Vector 3)
// u_sgParams[1]: Foam Color (Vector 3)
// u_sgParams[2]: Fall Speed (Float)
// u_sgParams[3]: Base Height (Float)


void main()
{
	vec4 sg_fragCoord = gl_FragCoord;
	bool sg_frontFacing = gl_FrontFacing;
	vec3 sg_PositionObject = v_objectPos;
	vec3 sg_PositionWorld = v_worldPos;
	vec3 sg_NormalWorld = sgSafeNormalize(v_normal);
	vec3 sg_TangentWorld = sgSafeNormalize(v_tangent);
	vec3 sg_BitangentWorld = sgSafeNormalize(v_bitangent);
	float sg_Time = u_time.y;
	float sg_DeltaTime = u_time.x;

	// Split #7
	vec3 n7_In = sg_PositionObject;
	// Multiply #9
	float n9_Out = n7_In.x * 1.39999998;
	// Multiply #10
	float n10_Out = n7_In.z * 0.899999976;
	// Add #11
	float n11_Out = n9_Out + n10_Out;
	// Multiply #12
	float n12_Out = n7_In.y * 0.159999996;
	// Multiply #13
	float n13_Out = sg_Time * u_sgParams[2].x;
	// Add #14
	float n14_Out = n12_Out + n13_Out;
	// Combine #15
	vec4 n15_RGBA = vec4(n11_Out, n14_Out, 0.0, 1.0);
	// Gradient Noise #16
	float n16_Out = sgGradientNoise(n15_RGBA.xy, 3.0);
	// Multiply #19
	float n19_Out = n16_Out * 0.649999976;
	// Tiling And Offset #17
	vec2 n17_Out = n15_RGBA.xy * vec2(2.29999995, 1.60000002) + vec2(0.400000006, 0.0);
	// Gradient Noise #18
	float n18_Out = sgGradientNoise(n17_Out, 3.0);
	// Multiply #20
	float n20_Out = n18_Out * 0.349999994;
	// Add #21
	float n21_Out = n19_Out + n20_Out;
	// Smoothstep #25
	float n25_Out = smoothstep(0.400000006, 0.680000007, n21_Out);
	// Add #22
	float n22_Out = u_sgParams[3].x + 2.5;
	// Smoothstep #23
	float n23_Out = smoothstep(u_sgParams[3].x, n22_Out, n7_In.y);
	// One Minus #24
	float n24_Out = 1.0 - n23_Out;
	// Add #26
	float n26_Out = n25_Out + n24_Out;
	// Saturate #27
	float n27_Out = clamp(n26_Out, 0.0, 1.0);
	// Lerp #28
	vec3 n28_Out = mix(u_sgParams[0].xyz, u_sgParams[1].xyz, vec3_splat(n27_Out));
	// Normal From Height #33
	vec3 n33_Out = sgWorldToTangent(sgNormalFromHeight(n21_Out, 0.400000006, sg_PositionWorld, sg_NormalWorld), sg_TangentWorld, sg_BitangentWorld, sg_NormalWorld);
	// Lerp #31
	float n31_Out = mix(0.449999988, 0.959999979, n27_Out);
	// Smoothstep #29
	float n29_Out = smoothstep((-0.899999976), 0.0500000007, n7_In.y);
	// One Minus #30
	float n30_Out = 1.0 - n29_Out;
	// Multiply #32
	float n32_Out = n31_Out * n30_Out;
	// Outputs
	vec3 sgOut_BaseColor = n28_Out;
	vec3 sgOut_Normal = n33_Out;
	float sgOut_Metallic = 0.0;
	float sgOut_Roughness = 0.300000012;
	vec3 sgOut_Emission = vec3(0.0, 0.0, 0.0);
	float sgOut_Occlusion = 1.0;
	float sgOut_Alpha = n32_Out;
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
