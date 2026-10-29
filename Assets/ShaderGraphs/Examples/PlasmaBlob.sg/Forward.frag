$input v_worldPos, v_normal, v_tangent, v_bitangent, v_texcoord0, v_viewPos, v_objectPos, v_objectNormal

// Generated from Assets/ShaderGraphs/Examples/PlasmaBlob.shadergraph by the shader graph compiler: edit the graph, not this file.
#define SG_NORMAL_WORLD 1

#include "Common.sh"
#include "StandardSurface.sh"
#include "ShaderGraph/SGLib.sh"
#include "Dither.sh"

uniform vec4 u_drawParams; // x screen-door fade (Dither.sh), per draw

uniform vec4 u_sgParams[16];
// u_sgParams[0]: Amplitude (Float)
// u_sgParams[1]: Noise Scale (Float)
// u_sgParams[2]: Flow Speed (Float)
// u_sgParams[3]: Pulse Speed (Float)
// u_sgParams[4]: Glow Color (Vector 3)
// u_sgParams[5]: Glow (Float)
// u_sgParams[6]: Hue Speed (Float)
// u_sgParams[7]: Crust Color (Vector 3)


void main()
{
	if (ditherDrops(u_drawParams.x, gl_FragCoord.xy))
	{
		discard;
	}
	vec4 sg_fragCoord = gl_FragCoord;
	bool sg_frontFacing = gl_FrontFacing;
	vec3 sg_PositionWorld = v_worldPos;
	vec3 sg_NormalObject = sgSafeNormalize(v_objectNormal);
	vec3 sg_CameraPosition = mul(u_invView, vec4(0.0, 0.0, 0.0, 1.0)).xyz;
	vec3 sg_ViewDirectionWorld = sgSafeNormalize(sg_CameraPosition - v_worldPos);
	float sg_Time = u_time.y;
	float sg_DeltaTime = u_time.x;

	// Swizzle .xy #17
	vec2 n17_Out = (vec4(sg_NormalObject, 1.0)).xy;
	// Multiply #12
	float n12_Out = sg_Time * u_sgParams[2].x;
	// Multiply #13
	float n13_Out = n12_Out * 0.600000024;
	// Combine #14
	vec4 n14_RGBA = vec4(n12_Out, n13_Out, 0.0, 1.0);
	// Add #18
	vec2 n18_Out = n17_Out + n14_RGBA.xy;
	// Fractal Noise #19
	float n19_Out = sgFractalNoise(n18_Out, u_sgParams[1].x, 4.0, 2.0, 0.5);
	// Swizzle .yz #20
	vec2 n20_Out = (vec4(sg_NormalObject, 1.0)).yz;
	// Multiply #15
	float n15_Out = n12_Out * (-0.5);
	// Combine #16
	vec4 n16_RGBA = vec4(n15_Out, n12_Out, 0.0, 1.0);
	// Add #21
	vec2 n21_Out = n20_Out + n16_RGBA.xy;
	// Fractal Noise #22
	float n22_Out = sgFractalNoise(n21_Out, u_sgParams[1].x, 4.0, 2.0, 0.5);
	// Add #23
	float n23_Out = n19_Out + n22_Out;
	// Multiply #24
	float n24_Out = n23_Out * 0.5;
	// Smoothstep #25
	float n25_Out = smoothstep(0.300000012, 0.550000012, n24_Out);
	// Multiply #26
	float n26_Out = sg_Time * u_sgParams[3].x;
	// Sine #27
	float n27_Out = sin(n26_Out);
	// Remap #28
	float n28_Out = 0.550000012 + (n27_Out - (-1.0)) * (1.14999998 - 0.550000012) / (1.0 - (-1.0));
	// DDX #33
	vec3 n33_Out = dFdx(sg_PositionWorld);
	// DDY #34
	vec3 n34_Out = dFdy(sg_PositionWorld);
	// Cross Product #35
	vec3 n35_Out = cross(n33_Out, n34_Out);
	// Normalize #36
	vec3 n36_Out = normalize(n35_Out);
	// Dot Product #38
	float n38_Out = dot(n36_Out, sg_ViewDirectionWorld);
	// Sign #39
	float n39_Out = sign(n38_Out);
	// Multiply #40
	vec3 n40_Out = n36_Out * vec3_splat(n39_Out);
	// Lerp #54
	float n54_Out = mix(0.600000024, 0.180000007, n25_Out);
	// Multiply #41
	float n41_Out = sg_Time * u_sgParams[6].x;
	// Hue #42
	vec3 n42_Out = sgHueShift(u_sgParams[4].xyz, n41_Out);
	// One Minus #43
	float n43_Out = 1.0 - n25_Out;
	// Power #44
	float n44_Out = pow(n43_Out, 6.0);
	// Multiply #45
	vec3 n45_Out = n42_Out * vec3_splat(n44_Out);
	// Multiply #46
	float n46_Out = u_sgParams[5].x * n28_Out;
	// Multiply #47
	vec3 n47_Out = n45_Out * vec3_splat(n46_Out);
	// Add #49
	float n49_Out = n41_Out + 0.5;
	// Hue #50
	vec3 n50_Out = sgHueShift(u_sgParams[4].xyz, n49_Out);
	// Fresnel Effect #51
	float n51_Out = pow(1.0 - clamp(dot(sgSafeNormalize(n40_Out), sgSafeNormalize(sg_ViewDirectionWorld)), 0.0, 1.0), 3.0);
	// Multiply #52
	float n52_Out = n51_Out * 0.600000024;
	// Multiply #53
	vec3 n53_Out = n50_Out * vec3_splat(n52_Out);
	// Add #55
	vec3 n55_Out = n47_Out + n53_Out;
	// Outputs
	vec3 sgOut_BaseColor = u_sgParams[7].xyz;
	vec3 sgOut_Normal = n40_Out;
	float sgOut_Metallic = 0.850000024;
	float sgOut_Roughness = n54_Out;
	vec3 sgOut_Emission = n55_Out;
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
