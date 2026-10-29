$input v_worldPos, v_normal, v_tangent, v_bitangent, v_texcoord0, v_viewPos, v_objectPos, v_objectNormal

// Generated from Assets/ShaderGraphs/Examples/RetroSun.shadergraph by the shader graph compiler: edit the graph, not this file.
#define SG_TRANSPARENT 1
#define SG_FOG 1

#include "Common.sh"
#include "Lighting.sh"
#include "Fog.sh"
#include "ShaderGraph/SGLib.sh"
#include "Dither.sh"

uniform vec4 u_drawParams; // x screen-door fade (Dither.sh), per draw

uniform vec4 u_sgParams[16];
// u_sgParams[0]: Top Color (Vector 3)
// u_sgParams[1]: Bottom Color (Vector 3)
// u_sgParams[2]: Stripes (Float)
// u_sgParams[3]: Stripe Speed (Float)
// u_sgParams[4]: Halo (Float)


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

	// Split #15
	vec2 n15_In = sg_UV0;
	// Remap #16
	float n16_Out = 0.0 + (n15_In.y - 0.166700006) * (1.0 - 0.0) / (0.833299994 - 0.166700006);
	// Saturate #28
	float n28_Out = clamp(n16_Out, 0.0, 1.0);
	// Lerp #29
	vec3 n29_Out = mix(u_sgParams[1].xyz, u_sgParams[0].xyz, vec3_splat(n28_Out));
	// Subtract #8
	vec2 n8_Out = sg_UV0 - vec2(0.5, 0.5);
	// Length #9
	float n9_Out = length(n8_Out);
	// Multiply #10
	float n10_Out = n9_Out * 3.0;
	// DDXY #11
	float n11_Out = fwidth(n10_Out);
	// Subtract #12
	float n12_Out = 1.0 - n11_Out;
	// Smoothstep #13
	float n13_Out = smoothstep(n12_Out, 1.0, n10_Out);
	// One Minus #14
	float n14_Out = 1.0 - n13_Out;
	// Subtract #22
	float n22_Out = 0.550000012 - n16_Out;
	// Multiply #23
	float n23_Out = n22_Out * 1.60000002;
	// Saturate #24
	float n24_Out = clamp(n23_Out, 0.0, 1.0);
	// Multiply #25
	float n25_Out = n24_Out * 0.850000024;
	// Add #26
	float n26_Out = n25_Out + 0.0599999987;
	// Multiply #18
	float n18_Out = n16_Out * u_sgParams[2].x;
	// Multiply #19
	float n19_Out = sg_Time * u_sgParams[3].x;
	// Add #20
	float n20_Out = n18_Out + n19_Out;
	// Fraction #21
	float n21_Out = fract(n20_Out);
	// Smoothstep #27
	float n27_Out = smoothstep(n25_Out, n26_Out, n21_Out);
	// Multiply #35
	float n35_Out = n14_Out * n27_Out;
	// Multiply #36
	vec3 n36_Out = n29_Out * vec3_splat(n35_Out);
	// Subtract #30
	float n30_Out = 1.5 - n10_Out;
	// Saturate #31
	float n31_Out = clamp(n30_Out, 0.0, 1.0);
	// Multiply #32
	float n32_Out = n31_Out * 2.0;
	// Power #33
	float n33_Out = pow(n32_Out, 4.0);
	// Multiply #34
	float n34_Out = n33_Out * u_sgParams[4].x;
	// Multiply #37
	vec3 n37_Out = u_sgParams[1].xyz * vec3_splat(n34_Out);
	// Add #38
	vec3 n38_Out = n36_Out + n37_Out;
	// Outputs
	vec3 sgOut_Color = n38_Out;
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
