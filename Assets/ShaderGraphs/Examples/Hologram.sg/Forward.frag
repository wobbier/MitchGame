$input v_worldPos, v_normal, v_tangent, v_bitangent, v_texcoord0, v_viewPos, v_objectPos, v_objectNormal

// Generated from Assets/ShaderGraphs/Examples/Hologram.shadergraph by the shader graph compiler: edit the graph, not this file.
#define SG_TRANSPARENT 1
#define SG_FOG 1

#include "Common.sh"
#include "Lighting.sh"
#include "Fog.sh"
#include "ShaderGraph/SGLib.sh"
#include "Dither.sh"

uniform vec4 u_drawParams; // x screen-door fade (Dither.sh), per draw

uniform vec4 u_sgParams[16];
// u_sgParams[0]: Tint (Vector 3)


void main()
{
	if (ditherDrops(u_drawParams.x, gl_FragCoord.xy))
	{
		discard;
	}
	vec4 sg_fragCoord = gl_FragCoord;
	bool sg_frontFacing = gl_FrontFacing;
	vec3 sg_PositionWorld = v_worldPos;
	vec3 sg_NormalWorld = sgSafeNormalize(v_normal);
	vec3 sg_CameraPosition = mul(u_invView, vec4(0.0, 0.0, 0.0, 1.0)).xyz;
	vec3 sg_ViewDirectionWorld = sgSafeNormalize(sg_CameraPosition - v_worldPos);
	float sg_Time = u_time.y;
	float sg_DeltaTime = u_time.x;

	// Fresnel Effect #3
	float n3_Out = pow(1.0 - clamp(dot(sgSafeNormalize(sg_NormalWorld), sgSafeNormalize(sg_ViewDirectionWorld)), 0.0, 1.0), 2.5);
	// Add #17
	float n17_Out = n3_Out + 0.150000006;
	// Split #5
	vec3 n5_In = sg_PositionWorld;
	// Multiply #8
	float n8_Out = n5_In.y * 24.0;
	// Multiply #7
	float n7_Out = sg_Time * 0.600000024;
	// Add #9
	float n9_Out = n8_Out + n7_Out;
	// Fraction #10
	float n10_Out = fract(n9_Out);
	// Step #11
	float n11_Out = step(0.5, n10_Out);
	// Remap #12
	float n12_Out = 0.349999994 + (n11_Out - 0.0) * (1.0 - 0.349999994) / (1.0 - 0.0);
	// Multiply #18
	float n18_Out = n17_Out * n12_Out;
	// Combine #14
	vec4 n14_RGBA = vec4(sg_Time, 0.0, 0.0, 1.0);
	// Multiply #15
	vec2 n15_Out = n14_RGBA.xy * vec2(8.0, 8.0);
	// Simplex Noise #13
	float n13_Out = sgSimplexNoise(n15_Out, 1.0);
	// Remap #16
	float n16_Out = 0.699999988 + (n13_Out - 0.0) * (1.20000005 - 0.699999988) / (1.0 - 0.0);
	// Multiply #19
	float n19_Out = n18_Out * n16_Out;
	// Multiply #20
	vec3 n20_Out = u_sgParams[0].xyz * vec3_splat(n19_Out);
	// Multiply #21
	vec3 n21_Out = n20_Out * vec3(2.5, 2.5, 2.5);
	// Outputs
	vec3 sgOut_Color = n21_Out;
	float sgOut_Alpha = n19_Out;
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
