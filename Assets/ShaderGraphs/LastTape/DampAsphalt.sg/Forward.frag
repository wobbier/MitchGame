$input v_worldPos, v_normal, v_tangent, v_bitangent, v_texcoord0, v_viewPos, v_objectPos, v_objectNormal

// Generated from Assets/ShaderGraphs/LastTape/DampAsphalt.shadergraph by the shader graph compiler: edit the graph, not this file.

#include "Common.sh"
#include "StandardSurface.sh"
#include "ShaderGraph/SGLib.sh"
#include "Dither.sh"

uniform vec4 u_drawParams; // x screen-door fade (Dither.sh), per draw

uniform vec4 u_sgParams[16];
// u_sgParams[0]: Dampness (Float)

void sgCustom_SummerRain_41112(vec3 World, float Wet, out vec3 Albedo, out float Roughness, out vec3 Normal)
{
vec2 p = World.xz;
float grit = fract(sin(dot(floor(p*160.0),vec2(12.9898,78.233)))*43758.5453);
float wetPatch = sgValueNoise(p*.37,1.0);
float damp = smoothstep(.36,.68,wetPatch)*Wet;
Albedo = mix(vec3(.055,.068,.083),vec3(.022,.033,.044),damp) * (.82+grit*.3);
Roughness = mix(.88,.23,damp);
Normal = normalize(vec3((grit-.5)*.045,(wetPatch-.5)*.045,1.0));
}


void main()
{
	if (ditherDrops(u_drawParams.x, gl_FragCoord.xy))
	{
		discard;
	}
	vec4 sg_fragCoord = gl_FragCoord;
	bool sg_frontFacing = gl_FrontFacing;
	vec3 sg_PositionWorld = v_worldPos;

	// SummerRain #4
	vec3 n4_Albedo;
	float n4_Roughness;
	vec3 n4_Normal;
	sgCustom_SummerRain_41112(sg_PositionWorld, u_sgParams[0].x, n4_Albedo, n4_Roughness, n4_Normal);
	// Outputs
	vec3 sgOut_BaseColor = n4_Albedo;
	vec3 sgOut_Normal = n4_Normal;
	float sgOut_Metallic = 0.0;
	float sgOut_Roughness = n4_Roughness;
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
