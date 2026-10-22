$input v_worldPos, v_normal, v_tangent, v_bitangent, v_texcoord0, v_viewPos, v_objectPos, v_objectNormal

// Generated from Assets/ShaderGraphs/LaunchNight/ArcadeScreen.shadergraph by the shader graph compiler: edit the graph, not this file.

#include "Common.sh"
#include "StandardSurface.sh"
#include "ShaderGraph/SGLib.sh"

uniform vec4 u_sgParams[16];
SAMPLER2D(s_sgTex0, 0); // Screen
// u_sgParams[0]: Brightness (Float)


void main()
{
	vec4 sg_fragCoord = gl_FragCoord;
	bool sg_frontFacing = gl_FrontFacing;
	vec2 sg_UV0 = v_texcoord0;
	float sg_Time = u_time.y;
	float sg_DeltaTime = u_time.x;

	// Panner #5
	vec2 n5_Out = sg_UV0 + vec2(0.0, 0.0299999993) * sg_Time;
	// Sample Texture 2D #6
	vec4 n6_RGBA = toLinear(texture2D(s_sgTex0, n5_Out));
	// Split #12
	vec2 n12_In = sg_UV0;
	// Multiply #13
	float n13_Out = n12_In.y * 1400.0;
	// Sine #14
	float n14_Out = sin(n13_Out);
	// Multiply #15
	float n15_Out = n14_Out * 0.200000003;
	// Add #16
	float n16_Out = 0.800000012 + n15_Out;
	// Multiply #8
	float n8_Out = sg_Time * 37.0;
	// Sine #9
	float n9_Out = sin(n8_Out);
	// Multiply #10
	float n10_Out = n9_Out * 0.0599999987;
	// Add #11
	float n11_Out = 0.899999976 + n10_Out;
	// Multiply #17
	float n17_Out = n16_Out * n11_Out;
	// Multiply #18
	vec3 n18_Out = n6_RGBA.xyz * vec3_splat(n17_Out);
	// Multiply #19
	vec3 n19_Out = n18_Out * vec3_splat(u_sgParams[0].x);
	// Outputs
	vec3 sgOut_BaseColor = vec3(0.0199999996, 0.0199999996, 0.0199999996);
	vec3 sgOut_Normal = vec3(0.0, 0.0, 1.0);
	float sgOut_Metallic = 0.0;
	float sgOut_Roughness = 0.100000001;
	vec3 sgOut_Emission = n19_Out;
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
