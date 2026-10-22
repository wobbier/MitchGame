$input v_worldPos, v_normal, v_tangent, v_bitangent, v_texcoord0, v_viewPos, v_objectPos, v_objectNormal

// Generated from Assets/ShaderGraphs/LaunchNight/BlinkLight.shadergraph by the shader graph compiler: edit the graph, not this file.

#include "Common.sh"
#include "StandardSurface.sh"
#include "ShaderGraph/SGLib.sh"

uniform vec4 u_sgParams[16];
// u_sgParams[0]: Color (Vector 3)
// u_sgParams[1]: Intensity (Float)
// u_sgParams[2]: Rate (Float)
// u_sgParams[3]: Duty (Float)
// u_sgParams[4]: Phase (Float)


void main()
{
	vec4 sg_fragCoord = gl_FragCoord;
	bool sg_frontFacing = gl_FrontFacing;
	float sg_Time = u_time.y;
	float sg_DeltaTime = u_time.x;

	// Multiply #12
	vec3 n12_Out = u_sgParams[0].xyz * vec3_splat(u_sgParams[1].x);
	// Multiply #8
	float n8_Out = sg_Time * u_sgParams[2].x;
	// Add #9
	float n9_Out = n8_Out + u_sgParams[4].x;
	// Fraction #10
	float n10_Out = fract(n9_Out);
	// Step #11
	float n11_Out = step(n10_Out, u_sgParams[3].x);
	// Multiply #13
	vec3 n13_Out = n12_Out * vec3_splat(n11_Out);
	// Outputs
	vec3 sgOut_BaseColor = vec3(0.0500000007, 0.0199999996, 0.0199999996);
	vec3 sgOut_Normal = vec3(0.0, 0.0, 1.0);
	float sgOut_Metallic = 0.0;
	float sgOut_Roughness = 0.300000012;
	vec3 sgOut_Emission = n13_Out;
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
