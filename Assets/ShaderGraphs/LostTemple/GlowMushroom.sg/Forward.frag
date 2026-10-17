$input v_worldPos, v_normal, v_tangent, v_bitangent, v_texcoord0, v_viewPos, v_objectPos, v_objectNormal

// Generated from Assets/ShaderGraphs/LostTemple/GlowMushroom.shadergraph by the shader graph compiler: edit the graph, not this file.

#include "Common.sh"
#include "StandardSurface.sh"
#include "ShaderGraph/SGLib.sh"

uniform vec4 u_sgParams[16];
SAMPLER2D(s_sgTex0, 0); // Albedo
// u_sgParams[0]: Glow Color (Vector 3)
// u_sgParams[1]: Glow Intensity (Float)
// u_sgParams[2]: Cap Height (Float)


void main()
{
	vec4 sg_fragCoord = gl_FragCoord;
	bool sg_frontFacing = gl_FrontFacing;
	vec2 sg_UV0 = v_texcoord0;
	vec3 sg_PositionObject = v_objectPos;
	vec3 sg_PositionWorld = v_worldPos;
	float sg_Time = u_time.y;
	float sg_DeltaTime = u_time.x;

	// Sample Texture 2D #21
	vec4 n21_RGBA = toLinear(texture2D(s_sgTex0, sg_UV0));
	// Multiply #22
	vec3 n22_Out = n21_RGBA.xyz * u_sgParams[0].xyz;
	// Add #10
	float n10_Out = u_sgParams[2].x + 0.119999997;
	// Split #7
	vec3 n7_In = sg_PositionObject;
	// Smoothstep #11
	float n11_Out = smoothstep(u_sgParams[2].x, n10_Out, n7_In.y);
	// Multiply #23
	float n23_Out = n11_Out * 0.600000024;
	// Lerp #24
	vec3 n24_Out = mix(n21_RGBA.xyz, n22_Out, vec3_splat(n23_Out));
	// Multiply #25
	vec3 n25_Out = u_sgParams[0].xyz * vec3_splat(n11_Out);
	// Multiply #13
	float n13_Out = sg_Time * 1.29999995;
	// Split #9
	vec3 n9_In = sg_PositionWorld;
	// Multiply #14
	float n14_Out = n9_In.x * 2.0999999;
	// Multiply #15
	float n15_Out = n9_In.z * 1.70000005;
	// Add #16
	float n16_Out = n14_Out + n15_Out;
	// Add #17
	float n17_Out = n13_Out + n16_Out;
	// Sine #18
	float n18_Out = sin(n17_Out);
	// Multiply #19
	float n19_Out = n18_Out * 0.5;
	// Add #20
	float n20_Out = n19_Out + 0.5;
	// Multiply #26
	float n26_Out = n20_Out * 0.649999976;
	// Add #27
	float n27_Out = 0.349999994 + n26_Out;
	// Multiply #28
	float n28_Out = u_sgParams[1].x * n27_Out;
	// Multiply #29
	vec3 n29_Out = n25_Out * vec3_splat(n28_Out);
	// Outputs
	vec3 sgOut_BaseColor = n24_Out;
	vec3 sgOut_Normal = vec3(0.0, 0.0, 1.0);
	float sgOut_Metallic = 0.0;
	float sgOut_Roughness = 0.449999988;
	vec3 sgOut_Emission = n29_Out;
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
