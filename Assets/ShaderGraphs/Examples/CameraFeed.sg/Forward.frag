$input v_worldPos, v_normal, v_tangent, v_bitangent, v_texcoord0, v_viewPos, v_objectPos, v_objectNormal

// Generated from Assets/ShaderGraphs/Examples/CameraFeed.shadergraph by the shader graph compiler: edit the graph, not this file.

#include "Common.sh"
#include "StandardSurface.sh"
#include "ShaderGraph/SGLib.sh"
#include "Dither.sh"

uniform vec4 u_drawParams; // x screen-door fade (Dither.sh), per draw

uniform vec4 u_sgParams[16];
SAMPLER2D(s_sgTex0, 0); // Feed
// u_sgParams[0]: Brightness (Float)


void main()
{
	if (ditherDrops(u_drawParams.x, gl_FragCoord.xy))
	{
		discard;
	}
	vec4 sg_fragCoord = gl_FragCoord;
	bool sg_frontFacing = gl_FrontFacing;
	vec2 sg_UV0 = v_texcoord0;

	// Tiling And Offset #3
	vec2 n3_Out = sg_UV0 * vec2(1.0, -1.0) + vec2(0.0, 1.0);
	// Sample Texture 2D #4
	vec4 n4_RGBA = toLinear(texture2D(s_sgTex0, n3_Out));
	// Split #6
	vec2 n6_In = sg_UV0;
	// Multiply #7
	float n7_Out = n6_In.y * 900.0;
	// Sine #8
	float n8_Out = sin(n7_Out);
	// Multiply #9
	float n9_Out = n8_Out * 0.100000001;
	// Add #10
	float n10_Out = 0.899999976 + n9_Out;
	// Multiply #11
	vec3 n11_Out = n4_RGBA.xyz * vec3_splat(n10_Out);
	// Multiply #13
	vec3 n13_Out = n11_Out * vec3_splat(u_sgParams[0].x);
	// Outputs
	vec3 sgOut_BaseColor = vec3(0.0199999996, 0.0199999996, 0.0199999996);
	vec3 sgOut_Normal = vec3(0.0, 0.0, 1.0);
	float sgOut_Metallic = 0.0;
	float sgOut_Roughness = 0.150000006;
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
