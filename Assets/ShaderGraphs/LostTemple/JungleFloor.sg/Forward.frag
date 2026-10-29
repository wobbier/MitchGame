$input v_worldPos, v_normal, v_tangent, v_bitangent, v_texcoord0, v_viewPos, v_objectPos, v_objectNormal

// Generated from Assets/ShaderGraphs/LostTemple/JungleFloor.shadergraph by the shader graph compiler: edit the graph, not this file.

#include "Common.sh"
#include "StandardSurface.sh"
#include "ShaderGraph/SGLib.sh"
#include "Dither.sh"

uniform vec4 u_drawParams; // x screen-door fade (Dither.sh), per draw

uniform vec4 u_sgParams[16];
SAMPLER2D(s_sgTex0, 0); // Dirt Texture
SAMPLER2D(s_sgTex1, 1); // Grass Texture
SAMPLER2D(s_sgTex2, 2); // Grass Normals
// u_sgParams[0]: Dirt Tint (Vector 3)
// u_sgParams[1]: Grass Tint (Vector 3)
// u_sgParams[2]: Tile (Float)
// u_sgParams[3]: Pool Center (Vector 3)
// u_sgParams[4]: Pool Radius (Float)
// u_sgParams[5]: Grass Amount (Float)


void main()
{
	if (ditherDrops(u_drawParams.x, gl_FragCoord.xy))
	{
		discard;
	}
	vec4 sg_fragCoord = gl_FragCoord;
	bool sg_frontFacing = gl_FrontFacing;
	vec3 sg_PositionWorld = v_worldPos;

	// Swizzle .xz #12
	vec2 n12_Out = (vec4(sg_PositionWorld, 1.0)).xz;
	// Multiply #13
	vec2 n13_Out = n12_Out * vec2_splat(u_sgParams[2].x);
	// Sample Texture 2D #15
	vec4 n15_RGBA = toLinear(texture2D(s_sgTex0, n13_Out));
	// Multiply #16
	vec3 n16_Out = n15_RGBA.xyz * u_sgParams[0].xyz;
	// Tiling And Offset #14
	vec2 n14_Out = n13_Out * vec2(0.829999983, 0.829999983) + vec2(0.370000005, 0.109999999);
	// Sample Texture 2D #17
	vec4 n17_RGBA = toLinear(texture2D(s_sgTex1, n14_Out));
	// Multiply #18
	vec3 n18_Out = n17_RGBA.xyz * u_sgParams[1].xyz;
	// Subtract #20
	float n20_Out = 1.04999995 - u_sgParams[5].x;
	// Subtract #21
	float n21_Out = n20_Out - 0.0799999982;
	// Add #22
	float n22_Out = n20_Out + 0.0599999987;
	// Fractal Noise #19
	float n19_Out = sgFractalNoise(n12_Out, 0.0599999987, 5.0, 2.0, 0.5);
	// Smoothstep #23
	float n23_Out = smoothstep(n21_Out, n22_Out, n19_Out);
	// Lerp #29
	vec3 n29_Out = mix(n16_Out, n18_Out, vec3_splat(n23_Out));
	// Add #26
	float n26_Out = u_sgParams[4].x + 4.0;
	// Swizzle .xz #24
	vec2 n24_Out = (vec4(u_sgParams[3].xyz, 1.0)).xz;
	// Distance #25
	float n25_Out = distance(n12_Out, n24_Out);
	// Smoothstep #27
	float n27_Out = smoothstep(u_sgParams[4].x, n26_Out, n25_Out);
	// One Minus #28
	float n28_Out = 1.0 - n27_Out;
	// Lerp #30
	float n30_Out = mix(1.0, 0.419999987, n28_Out);
	// Multiply #31
	vec3 n31_Out = n29_Out * vec3_splat(n30_Out);
	// Sample Texture 2D (Normal) #35
	vec4 n35_Raw = texture2D(s_sgTex2, n14_Out);
	vec4 n35_RGBA = vec4(sgUnpackNormal(n35_Raw), n35_Raw.w);
	// Lerp #36
	vec3 n36_Out = mix(vec3(0.0, 0.0, 1.0), n35_RGBA.xyz, vec3_splat(n23_Out));
	// Normal Strength #37
	vec3 n37_Out = sgNormalStrength(n36_Out, 0.800000012);
	// Lerp #32
	float n32_Out = mix(0.970000029, 0.899999976, n23_Out);
	// Lerp #33
	float n33_Out = mix(n32_Out, 0.219999999, n28_Out);
	// Outputs
	vec3 sgOut_BaseColor = n31_Out;
	vec3 sgOut_Normal = n37_Out;
	float sgOut_Metallic = 0.0;
	float sgOut_Roughness = n33_Out;
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
