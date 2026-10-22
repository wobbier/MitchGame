$input v_worldPos, v_normal, v_tangent, v_bitangent, v_texcoord0, v_viewPos, v_objectPos, v_objectNormal

// Generated from Assets/ShaderGraphs/LaunchNight/RainGlass.shadergraph by the shader graph compiler: edit the graph, not this file.
#define SG_TRANSPARENT 1

#include "Common.sh"
#include "StandardSurface.sh"
#include "ShaderGraph/SGLib.sh"

uniform vec4 u_sgParams[16];
// u_sgParams[0]: Tint (Vector 3)
// u_sgParams[1]: Scale (Float)
// u_sgParams[2]: Opacity (Float)
// u_sgParams[3]: Drop Glint (Vector 3)

void sgCustom_RainDrops_95161(vec2 P, float Time, float Scale, out float Height)
{
vec2 p = P * Scale;
float h = 0.0;
{
    vec2 uv = p * 22.0;
    vec2 id = floor(uv);
    vec2 fp = fract(uv) - vec2_splat(0.5);
    float n = fract(sin(dot(id, vec2(12.9898, 78.233))) * 43758.5453);
    vec2 o = vec2(fract(n * 13.1), fract(n * 71.7)) - vec2_splat(0.5);
    float r = 0.1 + 0.16 * fract(n * 7.3);
    float life = fract(Time * (0.05 + 0.1 * fract(n * 3.7)) + n);
    float d = length(fp - o * 0.5);
    h = max(h, (1.0 - smoothstep(r * 0.4, r, d)) * step(0.72, n) * smoothstep(1.0, 0.7, life));
}
{
    float cw = 0.16;
    float colx = floor(p.x / cw);
    float n = fract(sin(colx * 78.233 + 1.3) * 43758.5453);
    float x = (fract(p.x / cw) - 0.5) * cw + sin(p.y * 6.0 + n * 6.28) * 0.012;
    float s = p.y / 0.9 + Time * (0.18 + 0.3 * n) + n * 7.0;
    float cycle = floor(s);
    float dy = (fract(s) - 0.5) * 0.9;
    float m = fract(sin((cycle + colx * 13.0) * 12.9898) * 43758.5453);
    float head = 1.0 - smoothstep(0.008, 0.016, length(vec2(x, dy * 0.75)));
    float trailMask = step(0.0, dy) * (1.0 - smoothstep(0.0, 0.32, dy));
    float trail = (1.0 - smoothstep(0.002, 0.005, abs(x))) * trailMask;
    float bead = fract(dy * 26.0);
    float beads = (1.0 - smoothstep(0.003, 0.007, length(vec2(x, (bead - 0.5) / 26.0)))) * trailMask * step(0.45, fract(sin(floor(dy * 26.0) + m * 40.0) * 917.3));
    h = max(h, (head + max(trail * 0.35, beads * 0.8)) * step(0.3, m));
}
Height = h;
}


void main()
{
	vec4 sg_fragCoord = gl_FragCoord;
	bool sg_frontFacing = gl_FrontFacing;
	vec3 sg_PositionWorld = v_worldPos;
	vec3 sg_NormalWorld = sgSafeNormalize(v_normal);
	vec3 sg_TangentWorld = sgSafeNormalize(v_tangent);
	vec3 sg_BitangentWorld = sgSafeNormalize(v_bitangent);
	float sg_Time = u_time.y;
	float sg_DeltaTime = u_time.x;

	// Split #6
	vec3 n6_In = sg_PositionWorld;
	// Add #8
	float n8_Out = n6_In.x + n6_In.z;
	// Combine #10
	vec4 n10_RGBA = vec4(n8_Out, n6_In.y, 0.0, 1.0);
	// RainDrops #12
	float n12_Height;
	sgCustom_RainDrops_95161(n10_RGBA.xy, sg_Time, u_sgParams[1].x, n12_Height);
	// Normal From Height #14
	vec3 n14_Out = sgWorldToTangent(sgNormalFromHeight(n12_Height, 0.800000012, sg_PositionWorld, sg_NormalWorld), sg_TangentWorld, sg_BitangentWorld, sg_NormalWorld);
	// Multiply #15
	vec3 n15_Out = u_sgParams[3].xyz * vec3_splat(n12_Height);
	// Multiply #16
	float n16_Out = n12_Height * 0.119999997;
	// Add #17
	float n17_Out = u_sgParams[2].x + n16_Out;
	// Saturate #18
	float n18_Out = clamp(n17_Out, 0.0, 1.0);
	// Outputs
	vec3 sgOut_BaseColor = u_sgParams[0].xyz;
	vec3 sgOut_Normal = n14_Out;
	float sgOut_Metallic = 0.0;
	float sgOut_Roughness = 0.0500000007;
	vec3 sgOut_Emission = n15_Out;
	float sgOut_Occlusion = 1.0;
	float sgOut_Alpha = n18_Out;
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
