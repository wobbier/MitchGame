$input v_worldPos, v_normal, v_tangent, v_bitangent, v_texcoord0, v_viewPos, v_objectPos, v_objectNormal

// Generated from Assets/ShaderGraphs/Examples/Dissolve.shadergraph by the shader graph compiler: edit the graph, not this file.
#define SG_ALPHA_CLIP 1

#include "Common.sh"
#include "StandardSurface.sh"
#include "ShaderGraph/SGLib.sh"
#include "Dither.sh"

uniform vec4 u_drawParams; // x screen-door fade (Dither.sh), per draw

uniform vec4 u_sgParams[16];
// u_sgParams[0]: Edge Width (Float)
// u_sgParams[1]: Edge Color (Vector 3)
// u_sgParams[2]: Base Color (Vector 3)


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

	// Gradient Noise #2
	float n2_Out = sgGradientNoise(sg_UV0, 6.0);
	// Remap #8
	float n8_Out = 0.0500000007 + (sin(sg_Time) - (-1.0)) * (0.5 - 0.0500000007) / (1.0 - (-1.0));
	// Subtract #9
	float n9_Out = n2_Out - n8_Out;
	// Smoothstep #10
	float n10_Out = smoothstep(0.0, u_sgParams[0].x, n9_Out);
	// One Minus #11
	float n11_Out = 1.0 - n10_Out;
	// Multiply #12
	vec3 n12_Out = u_sgParams[1].xyz * vec3_splat(n11_Out);
	// Multiply #13
	vec3 n13_Out = n12_Out * vec3(6.4000001, 6.0, 6.0);
	// Outputs
	vec3 sgOut_BaseColor = u_sgParams[2].xyz;
	vec3 sgOut_Normal = vec3(0.0, 0.0, 1.0);
	float sgOut_Metallic = 0.0;
	float sgOut_Roughness = 0.349999994;
	vec3 sgOut_Emission = n13_Out;
	float sgOut_Occlusion = 1.0;
	float sgOut_Alpha = n9_Out;
	float sgOut_AlphaClipThreshold = 0.0;

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
