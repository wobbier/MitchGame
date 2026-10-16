$input v_worldPos, v_normal, v_tangent, v_bitangent, v_texcoord0, v_viewPos, v_objectPos, v_objectNormal

// Generated from Assets/ShaderGraphs/Examples/WindSway.shadergraph by the shader graph compiler: edit the graph, not this file.

#include "Common.sh"
#include "StandardSurface.sh"
#include "ShaderGraph/SGLib.sh"

uniform vec4 u_sgParams[16];
// u_sgParams[0]: Strength (Float)
// u_sgParams[1]: Speed (Float)


void main()
{
	vec4 sg_fragCoord = gl_FragCoord;
	bool sg_frontFacing = gl_FrontFacing;
	vec3 sg_PositionObject = v_objectPos;

	// Split #5
	vec3 n5_In = sg_PositionObject;
	// Saturate #12
	float n12_Out = clamp(n5_In.y, 0.0, 1.0);
	// Lerp #19
	vec3 n19_Out = mix(vec3(0.0799999982, 0.180000007, 0.0399999991), vec3(0.349999994, 0.550000012, 0.119999997), vec3_splat(n12_Out));
	// Outputs
	vec3 sgOut_BaseColor = n19_Out;
	vec3 sgOut_Normal = vec3(0.0, 0.0, 1.0);
	float sgOut_Metallic = 0.0;
	float sgOut_Roughness = 0.699999988;
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
