$input v_worldPos, v_normal, v_tangent, v_bitangent, v_texcoord0, v_viewPos, v_objectPos, v_objectNormal

// Generated from Assets/ShaderGraphs/Examples/SynthwaveTerrain.shadergraph by the shader graph compiler: edit the graph, not this file.
#define SG_OFFSET_WORLD 1
#define SG_FOG 1

#include "Common.sh"
#include "Lighting.sh"
#include "Fog.sh"
#include "ShaderGraph/SGLib.sh"
#include "Dither.sh"

uniform vec4 u_drawParams; // x screen-door fade (Dither.sh), per draw

uniform vec4 u_sgParams[16];
// u_sgParams[0]: Height (Float)
// u_sgParams[1]: Valley Width (Float)
// u_sgParams[2]: Noise Scale (Float)
// u_sgParams[3]: Speed (Float)
// u_sgParams[4]: Curvature (Float)
// u_sgParams[5]: Cell Size (Float)
// u_sgParams[6]: Line Width (Float)
// u_sgParams[7]: Low Color (Vector 3)
// u_sgParams[8]: High Color (Vector 3)
// u_sgParams[9]: Fill Color (Vector 3)


void main()
{
	if (ditherDrops(u_drawParams.x, gl_FragCoord.xy))
	{
		discard;
	}
	vec4 sg_fragCoord = gl_FragCoord;
	bool sg_frontFacing = gl_FrontFacing;
	vec3 sg_PositionWorld = v_worldPos;
	float sg_Time = u_time.y;
	float sg_DeltaTime = u_time.x;

	// Swizzle .xz #13
	vec2 n13_Out = (vec4(sg_PositionWorld, 1.0)).xz;
	// Multiply #15
	float n15_Out = sg_Time * u_sgParams[3].x;
	// Combine #16
	vec4 n16_RGBA = vec4(0.0, n15_Out, 0.0, 1.0);
	// Add #17
	vec2 n17_Out = n13_Out + n16_RGBA.xy;
	// Fractal Noise #18
	float n18_Out = sgFractalNoise(n17_Out, u_sgParams[2].x, 5.0, 2.0, 0.5);
	// Smoothstep #19
	float n19_Out = smoothstep(0.300000012, 0.850000024, n18_Out);
	// Add #21
	float n21_Out = u_sgParams[1].x + 10.0;
	// Split #20
	vec3 n20_In = sg_PositionWorld;
	// Absolute #22
	float n22_Out = abs(n20_In.x);
	// Smoothstep #23
	float n23_Out = smoothstep(u_sgParams[1].x, n21_Out, n22_Out);
	// Multiply #24
	float n24_Out = n19_Out * n23_Out;
	// Multiply #58
	float n58_Out = n24_Out * 3.0;
	// Add #59
	float n59_Out = n58_Out + 1.0;
	// Multiply #60
	vec3 n60_Out = u_sgParams[9].xyz * vec3_splat(n59_Out);
	// Lerp #55
	vec3 n55_Out = mix(u_sgParams[7].xyz, u_sgParams[8].xyz, vec3_splat(n24_Out));
	// Divide #33
	vec2 n33_Out = n17_Out / vec2_splat(u_sgParams[5].x);
	// Fraction #34
	vec2 n34_Out = fract(n33_Out);
	// One Minus #35
	vec2 n35_Out = 1.0 - n34_Out;
	// Minimum #36
	vec2 n36_Out = min(n34_Out, n35_Out);
	// DDXY #37
	vec2 n37_Out = fwidth(n33_Out);
	// Multiply #38
	vec2 n38_Out = n37_Out * vec2_splat(u_sgParams[6].x);
	// Divide #39
	vec2 n39_Out = n36_Out / n38_Out;
	// Saturate #40
	vec2 n40_Out = clamp(n39_Out, 0.0, 1.0);
	// One Minus #41
	vec2 n41_Out = 1.0 - n40_Out;
	// Split #42
	vec2 n42_In = n41_Out;
	// Maximum #47
	float n47_Out = max(n42_In.x, n42_In.y);
	// Split #43
	vec2 n43_In = n37_Out;
	// Maximum #44
	float n44_Out = max(n43_In.x, n43_In.y);
	// Smoothstep #45
	float n45_Out = smoothstep(0.0799999982, 0.300000012, n44_Out);
	// One Minus #46
	float n46_Out = 1.0 - n45_Out;
	// Multiply #48
	float n48_Out = n47_Out * n46_Out;
	// Multiply #56
	vec3 n56_Out = n55_Out * vec3_splat(n48_Out);
	// Split #49
	vec2 n49_In = n17_Out;
	// Multiply #50
	float n50_Out = n49_In.y * 0.0399999991;
	// Fraction #51
	float n51_Out = fract(n50_Out);
	// Power #52
	float n52_Out = pow(n51_Out, 10.0);
	// Multiply #53
	float n53_Out = n52_Out * 3.0;
	// Add #54
	float n54_Out = n53_Out + 1.0;
	// Multiply #57
	vec3 n57_Out = n56_Out * vec3_splat(n54_Out);
	// Add #61
	vec3 n61_Out = n60_Out + n57_Out;
	// Outputs
	vec3 sgOut_Color = n61_Out;
	float sgOut_Alpha = 1.0;
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
