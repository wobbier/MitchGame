$input v_worldPos, v_normal, v_tangent, v_bitangent, v_texcoord0, v_viewPos, v_objectPos, v_objectNormal

// Generated from Assets/ShaderGraphs/LaunchNight/Neon.shadergraph by the shader graph compiler: edit the graph, not this file.

#include "Common.sh"
#include "StandardSurface.sh"
#include "ShaderGraph/SGLib.sh"
#include "Dither.sh"

uniform vec4 u_drawParams; // x screen-door fade (Dither.sh), per draw

uniform vec4 u_sgParams[16];
SAMPLER2D(s_sgTex0, 0); // Albedo
// u_sgParams[0]: Neon Color (Vector 3)
// u_sgParams[1]: Intensity (Float)
// u_sgParams[2]: Flicker Rate (Float)
// u_sgParams[3]: Seed (Float)

void sgCustom_Buzz_83340(float Time, float Rate, float Seed, out float Buzz)
{
float t = Time * Rate;
float k = floor(t);
float n = fract(sin(k * 12.9898 + Seed) * 43758.5453);
float drop = step(0.9, n) * step(fract(t), 0.35);
Buzz = (1.0 - drop * 0.85) * (0.94 + 0.06 * sin(Time * 120.0));
}


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

	// Sample Texture 2D #7
	vec4 n7_RGBA = toLinear(texture2D(s_sgTex0, sg_UV0));
	// Split #8
	vec3 n8_In = n7_RGBA.xyz;
	// Maximum #9
	float n9_Out = max(n8_In.x, n8_In.y);
	// Maximum #10
	float n10_Out = max(n9_Out, n8_In.z);
	// Minimum #11
	float n11_Out = min(n8_In.x, n8_In.y);
	// Minimum #12
	float n12_Out = min(n11_Out, n8_In.z);
	// Subtract #13
	float n13_Out = n10_Out - n12_Out;
	// Smoothstep #14
	float n14_Out = smoothstep(0.25, 0.449999988, n13_Out);
	// Buzz #16
	float n16_Buzz;
	sgCustom_Buzz_83340(sg_Time, u_sgParams[2].x, u_sgParams[3].x, n16_Buzz);
	// Multiply #17
	float n17_Out = n14_Out * n16_Buzz;
	// Multiply #18
	vec3 n18_Out = u_sgParams[0].xyz * vec3_splat(n17_Out);
	// Multiply #19
	vec3 n19_Out = n18_Out * vec3_splat(u_sgParams[1].x);
	// Outputs
	vec3 sgOut_BaseColor = n7_RGBA.xyz;
	vec3 sgOut_Normal = vec3(0.0, 0.0, 1.0);
	float sgOut_Metallic = 0.0;
	float sgOut_Roughness = 0.349999994;
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
