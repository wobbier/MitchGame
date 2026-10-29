$input v_worldPos, v_normal, v_tangent, v_bitangent, v_texcoord0, v_viewPos, v_objectPos, v_objectNormal

// Generated from Assets/ShaderGraphs/LaunchNight/Lightning.shadergraph by the shader graph compiler: edit the graph, not this file.
#define SG_TRANSPARENT 1
#define SG_FOG 1

#include "Common.sh"
#include "Lighting.sh"
#include "Fog.sh"
#include "ShaderGraph/SGLib.sh"
#include "Dither.sh"

uniform vec4 u_drawParams; // x screen-door fade (Dither.sh), per draw

uniform vec4 u_sgParams[16];
// u_sgParams[0]: Bolt Color (Vector 3)
// u_sgParams[1]: Intensity (Float)
// u_sgParams[2]: Seed (Float)

void sgCustom_Bolt_21744(vec2 UV, float Time, float Seed, out float Glow)
{
float y = UV.y;
float path = 0.0;
float amp = 0.16;
float freq = 3.0;
for (int i = 0; i < 5; i++)
{
    float fi = float(i);
    float k = y * freq + Seed * (fi + 1.0) * 1.7;
    float a = fract(sin(floor(k) * 12.9898 + fi * 4.1 + Seed) * 43758.5453) - 0.5;
    float b = fract(sin((floor(k) + 1.0) * 12.9898 + fi * 4.1 + Seed) * 43758.5453) - 0.5;
    path += mix(a, b, fract(k)) * amp;
    amp *= 0.5;
    freq *= 2.3;
}
float d = abs(UV.x - 0.5 - path);
float branchY = clamp((y - 0.35) / 0.3, 0.0, 1.0);
float branch = abs(UV.x - 0.5 - path - branchY * 0.12 - sin(y * 47.0 + Seed) * 0.01);
branch = (1.0 - smoothstep(0.0, 0.004, branch)) * step(0.35, y) * step(y, 0.65) * (1.0 - branchY);
float core = 1.0 - smoothstep(0.0, 0.005, d);
float halo = exp(-d * 45.0) * 0.45;
float ends = smoothstep(0.0, 0.04, y) * smoothstep(1.0, 0.94, y);
float flick = 0.55 + 0.45 * step(0.4, fract(Time * 19.0));
Glow = (core + halo + branch) * ends * flick;
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

	// Bolt #7
	float n7_Glow;
	sgCustom_Bolt_21744(sg_UV0, sg_Time, u_sgParams[2].x, n7_Glow);
	// Multiply #8
	float n8_Out = n7_Glow * u_sgParams[1].x;
	// Multiply #9
	vec3 n9_Out = u_sgParams[0].xyz * vec3_splat(n8_Out);
	// Saturate #10
	float n10_Out = clamp(n8_Out, 0.0, 1.0);
	// Outputs
	vec3 sgOut_Color = n9_Out;
	float sgOut_Alpha = n10_Out;
	float sgOut_AlphaClipThreshold = 0.5;

#if SG_ALPHA_CLIP
	if (sgOut_Alpha < sgOut_AlphaClipThreshold)
	{
		discard;
	}
#endif

	vec3 color = sgOut_Color;
#if SG_FOG
	// Opaque surfaces are fogged by the fog pass; transparent ones (drawn after it) fog themselves.
	vec3 cameraPos = mul(u_invView, vec4(0.0, 0.0, 0.0, 1.0)).xyz;
	vec3 sunColor = u_lightParams.x > 0.5 ? directionalRadiance(0, v_worldPos) : vec3_splat(0.0);
	vec4 fog = fogForward(cameraPos, v_worldPos, sunColor, u_dirLightDirection[0].xyz);
	color = color * fog.a + fog.rgb;
#endif
	gl_FragColor = vec4(color, sgOut_Alpha);
}
