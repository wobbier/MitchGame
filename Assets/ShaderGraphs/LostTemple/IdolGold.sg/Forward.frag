$input v_worldPos, v_normal, v_tangent, v_bitangent, v_texcoord0, v_viewPos, v_objectPos, v_objectNormal

// Generated from Assets/ShaderGraphs/LostTemple/IdolGold.shadergraph by the shader graph compiler: edit the graph, not this file.

#include "Common.sh"
#include "StandardSurface.sh"
#include "ShaderGraph/SGLib.sh"

uniform vec4 u_sgParams[16];
// u_sgParams[0]: Gold Color (Vector 3)
// u_sgParams[1]: Glow Color (Vector 3)
// u_sgParams[2]: Glow Intensity (Float)
// u_sgParams[3]: Pulse Speed (Float)
// u_sgParams[4]: Vein Scale (Float)


void main()
{
	vec4 sg_fragCoord = gl_FragCoord;
	bool sg_frontFacing = gl_FrontFacing;
	vec3 sg_PositionObject = v_objectPos;
	float sg_Time = u_time.y;
	float sg_DeltaTime = u_time.x;

	// Split #8
	vec3 n8_In = sg_PositionObject;
	// Multiply #9
	float n9_Out = n8_In.z * 0.699999988;
	// Add #10
	float n10_Out = n8_In.x + n9_Out;
	// Combine #11
	vec4 n11_RGBA = vec4(n10_Out, n8_In.y, 0.0, 1.0);
	// Gradient Noise #28
	float n28_Out = sgGradientNoise(n11_RGBA.xy, 90.0);
	// Multiply #29
	float n29_Out = n28_Out * 0.219999999;
	// Add #30
	float n30_Out = 0.119999997 + n29_Out;
	// Gradient Noise #12
	float n12_Out = sgGradientNoise(n11_RGBA.xy, u_sgParams[4].x);
	// Multiply #13
	float n13_Out = n12_Out * 2.0;
	// Subtract #14
	float n14_Out = n13_Out - 1.0;
	// Absolute #15
	float n15_Out = abs(n14_Out);
	// One Minus #16
	float n16_Out = 1.0 - n15_Out;
	// Power #17
	float n17_Out = pow(n16_Out, 12.0);
	// Multiply #23
	vec3 n23_Out = u_sgParams[1].xyz * vec3_splat(n17_Out);
	// Multiply #19
	float n19_Out = sg_Time * u_sgParams[3].x;
	// Sine #20
	float n20_Out = sin(n19_Out);
	// Multiply #21
	float n21_Out = n20_Out * 0.5;
	// Add #22
	float n22_Out = n21_Out + 0.5;
	// Multiply #24
	float n24_Out = n22_Out * 0.699999988;
	// Add #25
	float n25_Out = 0.300000012 + n24_Out;
	// Multiply #26
	float n26_Out = u_sgParams[2].x * n25_Out;
	// Multiply #27
	vec3 n27_Out = n23_Out * vec3_splat(n26_Out);
	// Outputs
	vec3 sgOut_BaseColor = u_sgParams[0].xyz;
	vec3 sgOut_Normal = vec3(0.0, 0.0, 1.0);
	float sgOut_Metallic = 1.0;
	float sgOut_Roughness = n30_Out;
	vec3 sgOut_Emission = n27_Out;
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
