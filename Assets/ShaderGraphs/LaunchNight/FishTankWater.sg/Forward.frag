$input v_worldPos, v_normal, v_tangent, v_bitangent, v_texcoord0, v_viewPos, v_objectPos, v_objectNormal

// Generated from Assets/ShaderGraphs/LaunchNight/FishTankWater.shadergraph by the shader graph compiler: edit the graph, not this file.
#define SG_TRANSPARENT 1

#include "Common.sh"
#include "StandardSurface.sh"
#include "ShaderGraph/SGLib.sh"

uniform vec4 u_sgParams[16];
// u_sgParams[0]: Water Color (Vector 3)
// u_sgParams[1]: Glow (Float)


void main()
{
	vec4 sg_fragCoord = gl_FragCoord;
	bool sg_frontFacing = gl_FrontFacing;
	vec3 sg_PositionWorld = v_worldPos;
	vec3 sg_NormalWorld = sgSafeNormalize(v_normal);
	vec3 sg_CameraPosition = mul(u_invView, vec4(0.0, 0.0, 0.0, 1.0)).xyz;
	vec3 sg_ViewDirectionWorld = sgSafeNormalize(sg_CameraPosition - v_worldPos);
	float sg_Time = u_time.y;

	// Swizzle .xy #5
	vec2 n5_Out = (vec4(sg_PositionWorld, 1.0)).xy;
	// Swizzle .zz #6
	vec2 n6_Out = (vec4(sg_PositionWorld, 1.0)).zz;
	// Add #7
	vec2 n7_Out = n5_Out + n6_Out;
	// Multiply #8
	vec2 n8_Out = n7_Out * vec2(3.0, 3.0);
	// Panner #9
	vec2 n9_Out = n8_Out + vec2(0.0799999982, -0.119999997) * sg_Time;
	// Gradient Noise #10
	float n10_Out = sgGradientNoise(n9_Out, 6.0);
	// Power #11
	float n11_Out = pow(n10_Out, 3.0);
	// Multiply #12
	float n12_Out = n11_Out * u_sgParams[1].x;
	// Multiply #15
	vec4 n15_Out = vec4(0.0508760884, 0.692071199, 0.787412345, 1.0) * vec4_splat(n12_Out);
	// Fresnel Effect #13
	float n13_Out = pow(1.0 - clamp(dot(sgSafeNormalize(sg_NormalWorld), sgSafeNormalize(sg_ViewDirectionWorld)), 0.0, 1.0), 3.0);
	// Lerp #16
	float n16_Out = mix(0.379999995, 0.800000012, n13_Out);
	// Outputs
	vec3 sgOut_BaseColor = u_sgParams[0].xyz;
	vec3 sgOut_Normal = vec3(0.0, 0.0, 1.0);
	float sgOut_Metallic = 0.0;
	float sgOut_Roughness = 0.0500000007;
	vec3 sgOut_Emission = (n15_Out).xyz;
	float sgOut_Occlusion = 1.0;
	float sgOut_Alpha = n16_Out;
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
