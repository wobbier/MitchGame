// Generated from Assets/ShaderGraphs/LostTemple/RuneCircle.shadergraph by the shader graph compiler: edit the graph, not this file.
// Pairs with the engine's Decal.vert: the graph supplies the decal's surface, DecalCommon.sh
// projects and lights it like Decal.frag.
#define SG_TARGET_DECAL 1

#include "Common.sh"

SAMPLER2D(s_sgSceneDepth, 7);
#define DECAL_SCENE_DEPTH s_sgSceneDepth
#include "DecalCommon.sh"
#include "ShaderGraph/SGLib.sh"

// Linear view depth of the opaque scene under a screen UV.
float sgSceneDepth(vec2 _uv)
{
	return sceneViewPosition(_uv).z;
}

uniform vec4 u_sgParams[16];
// u_sgParams[0]: Glow Color (Vector 3)
// u_sgParams[1]: Glow Intensity (Float)
// u_sgParams[2]: Turn Speed (Float)
// u_sgParams[3]: Carving Color (Vector 3)

void sgCustom_RuneRing_23373(vec2 UV, float Time, float Speed, out float Mask, out float Glow)
{
vec2 p = UV - vec2_splat(0.5);
float r = length(p) * 2.0;
float a = atan2(p.y, p.x) * 0.15915494 + 0.5;
float ring = 1.0 - smoothstep(0.0, 0.012, abs(r - 0.94));
ring += 1.0 - smoothstep(0.0, 0.008, abs(r - 0.79));
ring += 1.0 - smoothstep(0.0, 0.01, abs(r - 0.43));
ring += (1.0 - smoothstep(0.0, 0.006, abs(r - 0.36))) * 0.6;
float turn = a + Time * Speed;
float cell = floor(turn * 28.0);
float seg = fract(turn * 28.0);
float h = fract(sin(cell * 91.7) * 4375.85);
float h2 = fract(sin(cell * 17.3 + 4.1) * 2953.31);
float band = step(0.815, r) * step(r, 0.915);
float stroke = step(0.22, seg) * step(seg, 0.32 + h * 0.45);
float bar = step(abs(r - (0.83 + h2 * 0.06)), 0.007) * step(0.2, seg) * step(seg, 0.8);
float glyph = band * max(stroke * step(0.3, h), bar);
float spin = a * 6.2831853 - Time * Speed * 2.5;
vec2 q = vec2(cos(spin), sin(spin)) * r;
float star = 0.0;
for (int i = 0; i < 6; i++)
{
    float k = float(i) * 1.0471976;
    vec2 d = vec2(cos(k), sin(k));
    star += 1.0 - smoothstep(0.0, 0.01, abs(dot(q, vec2(-d.y, d.x))));
}
star *= step(r, 0.43) * step(0.12, r);
float core = 1.0 - smoothstep(0.0, 0.1, r);
float pulse = 0.65 + 0.35 * sin(Time * 2.2 - r * 9.0);
Mask = clamp(ring + glyph + star * 0.8 + core, 0.0, 1.0) * step(r, 1.0);
Glow = Mask * pulse;
}


void main()
{
	vec4 sg_fragCoord = gl_FragCoord;
	DecalGeometry sgDecal;
	if (!decalGeometry(gl_FragCoord.xy, sgDecal))
	{
		discard;
	}
	vec2 sg_UV0 = sgDecal.uv;
	vec3 sg_PositionObject = sgDecal.local;
	float sg_Time = u_time.y;
	float sg_DeltaTime = u_time.x;
	float sg_DecalFade = sgDecal.fade;

	// RuneRing #8
	float n8_Mask;
	float n8_Glow;
	sgCustom_RuneRing_23373(sg_UV0, sg_Time, u_sgParams[2].x, n8_Mask, n8_Glow);
	// Multiply #10
	float n10_Out = n8_Mask * sg_DecalFade;
	// Multiply #11
	vec3 n11_Out = u_sgParams[0].xyz * vec3_splat(n8_Glow);
	// Multiply #12
	vec3 n12_Out = n11_Out * vec3_splat(u_sgParams[1].x);
	// Outputs
	vec3 sgOut_BaseColor = u_sgParams[3].xyz;
	float sgOut_Alpha = n10_Out;
	vec3 sgOut_Normal = vec3(0.0, 0.0, 1.0);
	float sgOut_Metallic = 0.0;
	float sgOut_Roughness = 0.600000024;
	vec3 sgOut_Emission = n12_Out;

	float alpha = sgOut_Alpha * sgDecal.fade;
	if (alpha <= 0.001)
	{
		discard;
	}
	vec3 N = decalWorldNormal(sgDecal, sgSafeNormalize(sgOut_Normal));
	vec3 color = shadeDecal(sgDecal, sgOut_BaseColor, N, sgOut_Metallic, sgOut_Roughness, sgOut_Emission, gl_FragCoord.xy);
	gl_FragColor = vec4(color, alpha);
}
