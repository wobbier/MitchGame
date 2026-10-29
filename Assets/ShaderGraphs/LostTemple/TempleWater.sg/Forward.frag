$input v_worldPos, v_normal, v_tangent, v_bitangent, v_texcoord0, v_viewPos, v_objectPos, v_objectNormal

// Generated from Assets/ShaderGraphs/LostTemple/TempleWater.shadergraph by the shader graph compiler: edit the graph, not this file.
#define SG_TRANSPARENT 1

#include "Common.sh"
#include "StandardSurface.sh"
#include "ShaderGraph/SGLib.sh"
#include "Dither.sh"

uniform vec4 u_drawParams; // x screen-door fade (Dither.sh), per draw

uniform vec4 u_sgParams[16];
// u_sgParams[0]: Deep Color (Vector 3)
// u_sgParams[1]: Shallow Color (Vector 3)
// u_sgParams[2]: Foam Center (Vector 3)
// u_sgParams[3]: Foam Radius (Float)
// u_sgParams[4]: Clarity (Float)


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
	vec3 sg_CameraPosition = mul(u_invView, vec4(0.0, 0.0, 0.0, 1.0)).xyz;
	vec3 sg_ViewDirectionWorld = sgSafeNormalize(sg_CameraPosition - v_worldPos);
	float sg_Time = u_time.y;

	// Fresnel Effect #18
	float n18_Out = pow(1.0 - clamp(dot(sgSafeNormalize(sg_NormalWorld), sgSafeNormalize(sg_ViewDirectionWorld)), 0.0, 1.0), 4.0);
	// Multiply #30
	float n30_Out = n18_Out * 0.800000012;
	// Lerp #31
	vec3 n31_Out = mix(u_sgParams[1].xyz, u_sgParams[0].xyz, vec3_splat(n30_Out));
	// Swizzle .xz #8
	vec2 n8_Out = (vec4(sg_PositionWorld, 1.0)).xz;
	// Multiply #19
	vec2 n19_Out = n8_Out * vec2(0.899999976, 0.899999976);
	// Panner #20
	vec2 n20_Out = n19_Out + vec2(0.0, -0.349999994) * sg_Time;
	// Gradient Noise #21
	float n21_Out = sgGradientNoise(n20_Out, 4.0);
	// Swizzle .xz #22
	vec2 n22_Out = (vec4(u_sgParams[2].xyz, 1.0)).xz;
	// Distance #23
	float n23_Out = distance(n8_Out, n22_Out);
	// Smoothstep #24
	float n24_Out = smoothstep(0.0, u_sgParams[3].x, n23_Out);
	// One Minus #25
	float n25_Out = 1.0 - n24_Out;
	// Multiply #26
	float n26_Out = n25_Out * 0.449999988;
	// Add #27
	float n27_Out = n21_Out + n26_Out;
	// Smoothstep #28
	float n28_Out = smoothstep(0.349999994, 0.699999988, n27_Out);
	// Multiply #29
	float n29_Out = n28_Out * n25_Out;
	// Lerp #33
	vec3 n33_Out = mix(n31_Out, vec3(0.850000024, 0.899999976, 0.899999976), vec3_splat(n29_Out));
	// Multiply #9
	vec2 n9_Out = n8_Out * vec2(0.180000007, 0.180000007);
	// Panner #10
	vec2 n10_Out = n9_Out + vec2(0.0350000001, 0.0199999996) * sg_Time;
	// Gradient Noise #11
	float n11_Out = sgGradientNoise(n10_Out, 7.0);
	// Multiply #14
	float n14_Out = n11_Out * 0.600000024;
	// Panner #12
	vec2 n12_Out = n9_Out + vec2(-0.0299999993, 0.0450000018) * sg_Time;
	// Gradient Noise #13
	float n13_Out = sgGradientNoise(n12_Out, 13.0);
	// Multiply #15
	float n15_Out = n13_Out * 0.400000006;
	// Add #16
	float n16_Out = n14_Out + n15_Out;
	// Normal From Height #17
	vec3 n17_Out = sgWorldToTangent(sgNormalFromHeight(n16_Out, 0.140000001, sg_PositionWorld, sg_NormalWorld), sg_TangentWorld, sg_BitangentWorld, sg_NormalWorld);
	// Lerp #37
	float n37_Out = mix(0.0399999991, 0.5, n29_Out);
	// Lerp #38
	float n38_Out = mix(0.400000006, 1.0, n29_Out);
	// One Minus #34
	float n34_Out = 1.0 - u_sgParams[4].x;
	// Lerp #35
	float n35_Out = mix(n34_Out, 0.959999979, n18_Out);
	// Maximum #36
	float n36_Out = max(n35_Out, n29_Out);
	// Outputs
	vec3 sgOut_BaseColor = n33_Out;
	vec3 sgOut_Normal = n17_Out;
	float sgOut_Metallic = 0.0;
	float sgOut_Roughness = n37_Out;
	vec3 sgOut_Emission = vec3(0.0, 0.0, 0.0);
	float sgOut_Occlusion = n38_Out;
	float sgOut_Alpha = n36_Out;
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
