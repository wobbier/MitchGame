$input v_worldPos, v_normal, v_tangent, v_bitangent, v_texcoord0, v_viewPos, v_objectPos, v_objectNormal

// Generated from Assets/ShaderGraphs/LostTemple/SpiritBeam.shadergraph by the shader graph compiler: edit the graph, not this file.
#define SG_TRANSPARENT 1

#include "Common.sh"
#include "Lighting.sh"
#include "Fog.sh"
#include "ShaderGraph/SGLib.sh"
#include "Dither.sh"

uniform vec4 u_drawParams; // x screen-door fade (Dither.sh), per draw

uniform vec4 u_sgParams[16];
// u_sgParams[0]: Beam Color (Vector 3)
// u_sgParams[1]: Intensity (Float)
// u_sgParams[2]: Rise Speed (Float)


void main()
{
	if (ditherDrops(u_drawParams.x, gl_FragCoord.xy))
	{
		discard;
	}
	vec4 sg_fragCoord = gl_FragCoord;
	bool sg_frontFacing = gl_FrontFacing;
	vec2 sg_UV0 = v_texcoord0;
	vec3 sg_PositionObject = v_objectPos;
	vec3 sg_NormalWorld = sgSafeNormalize(v_normal);
	vec3 sg_CameraPosition = mul(u_invView, vec4(0.0, 0.0, 0.0, 1.0)).xyz;
	vec3 sg_ViewDirectionWorld = sgSafeNormalize(sg_CameraPosition - v_worldPos);
	float sg_Time = u_time.y;
	float sg_DeltaTime = u_time.x;

	// Fresnel Effect #10
	float n10_Out = pow(1.0 - clamp(dot(sgSafeNormalize(sg_NormalWorld), sgSafeNormalize(sg_ViewDirectionWorld)), 0.0, 1.0), 1.5);
	// One Minus #11
	float n11_Out = 1.0 - n10_Out;
	// Multiply #22
	float n22_Out = n11_Out * n11_Out;
	// Split #6
	vec3 n6_In = sg_PositionObject;
	// Arctangent2 #12
	float n12_Out = atan2(n6_In.x, n6_In.z);
	// Multiply #13
	float n13_Out = n6_In.y * 1.5;
	// Multiply #15
	float n15_Out = sg_Time * u_sgParams[2].x;
	// Subtract #16
	float n16_Out = n13_Out - n15_Out;
	// Combine #17
	vec4 n17_RGBA = vec4(n12_Out, n16_Out, 0.0, 1.0);
	// Gradient Noise #18
	float n18_Out = sgGradientNoise(n17_RGBA.xy, 3.0);
	// Add #23
	float n23_Out = 0.349999994 + n18_Out;
	// Multiply #24
	float n24_Out = n22_Out * n23_Out;
	// Add #7
	float n7_Out = n6_In.y + 1.0;
	// Multiply #8
	float n8_Out = n7_Out * 0.5;
	// Saturate #9
	float n9_Out = clamp(n8_Out, 0.0, 1.0);
	// One Minus #19
	float n19_Out = 1.0 - n9_Out;
	// Smoothstep #20
	float n20_Out = smoothstep(0.0, 0.0799999982, n9_Out);
	// Multiply #21
	float n21_Out = n19_Out * n20_Out;
	// Multiply #25
	float n25_Out = n21_Out * u_sgParams[1].x;
	// Multiply #26
	float n26_Out = n24_Out * n25_Out;
	// Multiply #27
	vec3 n27_Out = u_sgParams[0].xyz * vec3_splat(n26_Out);
	// Saturate #28
	float n28_Out = clamp(n26_Out, 0.0, 1.0);
	// Gradient #30
	float n30_T = (sg_UV0).y;
	vec3 n30_Out = mix(vec3(0.0, 0.0, 0.0), vec3(1.0, 1.0, 1.0), vec3_splat(n30_T));
	// Multiply #29
	vec3 n29_Out = vec3_splat(n28_Out) * n30_Out;
	// Outputs
	vec3 sgOut_Color = n27_Out;
	float sgOut_Alpha = (n29_Out).x;
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
