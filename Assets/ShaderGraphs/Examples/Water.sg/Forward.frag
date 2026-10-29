$input v_worldPos, v_normal, v_tangent, v_bitangent, v_texcoord0, v_viewPos, v_objectPos, v_objectNormal

// Generated from Assets/ShaderGraphs/Examples/Water.shadergraph by the shader graph compiler: edit the graph, not this file.

#include "Common.sh"
#include "StandardSurface.sh"
#include "ShaderGraph/SGLib.sh"
#include "Dither.sh"

uniform vec4 u_drawParams; // x screen-door fade (Dither.sh), per draw

uniform vec4 u_sgParams[16];
// u_sgParams[0]: Deep Color (Vector 3)
// u_sgParams[1]: Shallow Color (Vector 3)


void main()
{
	if (ditherDrops(u_drawParams.x, gl_FragCoord.xy))
	{
		discard;
	}
	vec4 sg_fragCoord = gl_FragCoord;
	bool sg_frontFacing = gl_FrontFacing;
	vec2 sg_UV0 = v_texcoord0;
	vec3 sg_PositionWorld = v_worldPos;
	vec3 sg_NormalWorld = sgSafeNormalize(v_normal);
	vec3 sg_TangentWorld = sgSafeNormalize(v_tangent);
	vec3 sg_BitangentWorld = sgSafeNormalize(v_bitangent);
	vec3 sg_CameraPosition = mul(u_invView, vec4(0.0, 0.0, 0.0, 1.0)).xyz;
	vec3 sg_ViewDirectionWorld = sgSafeNormalize(sg_CameraPosition - v_worldPos);
	float sg_Time = u_time.y;

	// Fresnel Effect #11
	float n11_Out = pow(1.0 - clamp(dot(sgSafeNormalize(sg_NormalWorld), sgSafeNormalize(sg_ViewDirectionWorld)), 0.0, 1.0), 3.0);
	// Lerp #12
	vec3 n12_Out = mix(u_sgParams[0].xyz, u_sgParams[1].xyz, vec3_splat(n11_Out));
	// Panner #5
	vec2 n5_Out = sg_UV0 + vec2(0.0399999991, 0.0199999996) * sg_Time;
	// Gradient Noise #7
	float n7_Out = sgGradientNoise(n5_Out, 14.0);
	// Panner #6
	vec2 n6_Out = sg_UV0 + vec2(-0.0299999993, 0.0500000007) * sg_Time;
	// Gradient Noise #8
	float n8_Out = sgGradientNoise(n6_Out, 23.0);
	// Add #9
	float n9_Out = n7_Out + n8_Out;
	// Normal From Height #10
	vec3 n10_Out = sgWorldToTangent(sgNormalFromHeight(n9_Out, 0.0599999987, sg_PositionWorld, sg_NormalWorld), sg_TangentWorld, sg_BitangentWorld, sg_NormalWorld);
	// Outputs
	vec3 sgOut_BaseColor = n12_Out;
	vec3 sgOut_Normal = n10_Out;
	float sgOut_Metallic = 0.0;
	float sgOut_Roughness = 0.0599999987;
	vec3 sgOut_Emission = vec3(0.0, 0.0, 0.0);
	float sgOut_Occlusion = 1.0;
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
