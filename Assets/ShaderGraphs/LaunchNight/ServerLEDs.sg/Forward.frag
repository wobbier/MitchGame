$input v_worldPos, v_normal, v_tangent, v_bitangent, v_texcoord0, v_viewPos, v_objectPos, v_objectNormal

// Generated from Assets/ShaderGraphs/LaunchNight/ServerLEDs.shadergraph by the shader graph compiler: edit the graph, not this file.

#include "Common.sh"
#include "StandardSurface.sh"
#include "ShaderGraph/SGLib.sh"
#include "Dither.sh"

uniform vec4 u_drawParams; // x screen-door fade (Dither.sh), per draw

uniform vec4 u_sgParams[16];
// u_sgParams[0]: Seed (Float)
// u_sgParams[1]: Alarm (Float)
// u_sgParams[2]: Intensity (Float)

void sgCustom_Leds_73454(vec2 UV, float Time, float Seed, float Alarm, out vec3 Color)
{
vec2 grid = vec2(6.0, 44.0);
vec2 gp = UV * grid;
vec2 cell = floor(gp);
vec2 fp = fract(gp) - vec2_splat(0.5);
float h = fract(sin(dot(cell + vec2_splat(Seed * 17.0), vec2(12.9898, 78.233))) * 43758.5453);
float h2 = fract(h * 91.7);
float rate = 0.4 + h2 * 7.0;
float on = step(0.4, fract(Time * rate + h * 7.0));
float led = 1.0 - smoothstep(0.16, 0.3, length(fp * vec2(1.0, 0.5)));
vec3 col = h < 0.55 ? vec3(0.1, 1.0, 0.3) : (h < 0.82 ? vec3(1.0, 0.55, 0.08) : vec3(0.2, 0.5, 1.0));
float present = step(0.3, fract(h * 13.1)) * step(0.06, UV.y) * step(UV.y, 0.94);
float strobe = step(0.5, fract(Time * 2.2 + h * 0.15));
col = mix(col, vec3(1.0, 0.04, 0.02), Alarm);
on = mix(on, strobe, Alarm * step(0.25, h2));
Color = col * led * on * present;
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

	// Split #9
	vec2 n9_In = sg_UV0;
	// Multiply #10
	float n10_Out = n9_In.y * 44.0;
	// Fraction #11
	float n11_Out = fract(n10_Out);
	// Step #12
	float n12_Out = step(0.5, n11_Out);
	// Multiply #13
	float n13_Out = n12_Out * 0.400000006;
	// Add #14
	float n14_Out = 0.600000024 + n13_Out;
	// Multiply #15
	vec3 n15_Out = vec3_splat(n14_Out) * vec3(0.0399999991, 0.0450000018, 0.0500000007);
	// Leds #7
	vec3 n7_Color;
	sgCustom_Leds_73454(sg_UV0, sg_Time, u_sgParams[0].x, u_sgParams[1].x, n7_Color);
	// Multiply #16
	vec3 n16_Out = n7_Color * vec3_splat(u_sgParams[2].x);
	// Outputs
	vec3 sgOut_BaseColor = n15_Out;
	vec3 sgOut_Normal = vec3(0.0, 0.0, 1.0);
	float sgOut_Metallic = 0.600000024;
	float sgOut_Roughness = 0.349999994;
	vec3 sgOut_Emission = n16_Out;
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
