$input v_worldPos, v_normal, v_tangent, v_bitangent, v_texcoord0, v_viewPos, v_objectPos, v_objectNormal

// Generated from Assets/ShaderGraphs/LaunchNight/CityWindows.shadergraph by the shader graph compiler: edit the graph, not this file.

#include "Common.sh"
#include "StandardSurface.sh"
#include "ShaderGraph/SGLib.sh"

uniform vec4 u_sgParams[16];
// u_sgParams[0]: Facade (Vector 3)
// u_sgParams[1]: Intensity (Float)

void sgCustom_City_45628(vec3 P, vec3 N, float Time, out vec3 Emit, out float Window)
{
vec3 an = abs(N);
vec2 uv = an.x > an.z ? P.zy : P.xy;
vec2 gp = uv / vec2(3.1, 3.5);
vec2 id = floor(gp);
vec2 fp = fract(gp);
float win = step(0.16, fp.x) * step(fp.x, 0.84) * step(0.22, fp.y) * step(fp.y, 0.84);
float n = fract(sin(dot(id + floor(P.xz * 0.05) * 13.0, vec2(12.9898, 78.233)) + floor(an.x * 1.5) * 3.1) * 43758.5453);
float lit = step(0.64, n);
float tv = step(0.64, n) * step(n, 0.67) * (0.5 + 0.5 * sin(Time * (3.0 + n * 9.0) + n * 40.0));
vec3 warm = vec3(1.0, 0.72, 0.42);
vec3 cool = vec3(0.6, 0.78, 1.0);
vec3 col = fract(n * 31.7) < 0.7 ? warm : cool;
col = mix(col, vec3(0.3, 0.5, 1.0), step(0.0001, tv));
float side = step(an.y, 0.5);
Emit = col * win * lit * side * (0.4 + 0.6 * fract(n * 17.3)) * (1.0 - 0.6 * tv);
Window = win * side;
}


void main()
{
	vec4 sg_fragCoord = gl_FragCoord;
	bool sg_frontFacing = gl_FrontFacing;
	vec3 sg_PositionWorld = v_worldPos;
	vec3 sg_NormalWorld = sgSafeNormalize(v_normal);
	float sg_Time = u_time.y;
	float sg_DeltaTime = u_time.x;

	// City #7
	vec3 n7_Emit;
	float n7_Window;
	sgCustom_City_45628(sg_PositionWorld, sg_NormalWorld, sg_Time, n7_Emit, n7_Window);
	// Lerp #8
	vec3 n8_Out = mix(u_sgParams[0].xyz, vec3(0.0199999996, 0.0250000004, 0.0350000001), vec3_splat(n7_Window));
	// Multiply #10
	float n10_Out = n7_Window * 0.400000006;
	// Lerp #9
	float n9_Out = mix(0.800000012, 0.150000006, n7_Window);
	// Multiply #11
	vec3 n11_Out = n7_Emit * vec3_splat(u_sgParams[1].x);
	// Outputs
	vec3 sgOut_BaseColor = n8_Out;
	vec3 sgOut_Normal = vec3(0.0, 0.0, 1.0);
	float sgOut_Metallic = n10_Out;
	float sgOut_Roughness = n9_Out;
	vec3 sgOut_Emission = n11_Out;
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
