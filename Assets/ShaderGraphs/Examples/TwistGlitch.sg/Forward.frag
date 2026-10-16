$input v_worldPos, v_normal, v_tangent, v_bitangent, v_texcoord0, v_viewPos, v_objectPos, v_objectNormal

// Generated from Assets/ShaderGraphs/Examples/TwistGlitch.shadergraph by the shader graph compiler: edit the graph, not this file.
#define SG_NORMAL_WORLD 1

#include "Common.sh"
#include "StandardSurface.sh"
#include "ShaderGraph/SGLib.sh"

uniform vec4 u_sgParams[16];
// u_sgParams[0]: Twist (Float)
// u_sgParams[1]: Twist Speed (Float)
// u_sgParams[2]: Bands (Float)
// u_sgParams[3]: Glitch Rate (Float)
// u_sgParams[4]: Glitch Amount (Float)
// u_sgParams[5]: Glitch Distance (Float)
// u_sgParams[6]: Burst Rate (Float)
// u_sgParams[7]: Glitch Color A (Vector 3)
// u_sgParams[8]: Glitch Color B (Vector 3)


void main()
{
	vec4 sg_fragCoord = gl_FragCoord;
	bool sg_frontFacing = gl_FrontFacing;
	vec2 sg_UV0 = v_texcoord0;
	vec3 sg_PositionObject = v_objectPos;
	vec3 sg_PositionWorld = v_worldPos;
	vec3 sg_CameraPosition = mul(u_invView, vec4(0.0, 0.0, 0.0, 1.0)).xyz;
	vec3 sg_ViewDirectionWorld = sgSafeNormalize(sg_CameraPosition - v_worldPos);
	float sg_Time = u_time.y;
	float sg_DeltaTime = u_time.x;

	// Split #12
	vec3 n12_In = sg_PositionObject;
	// Multiply #19
	float n19_Out = n12_In.y * u_sgParams[2].x;
	// Floor #20
	float n20_Out = floor(n19_Out);
	// Add #25
	float n25_Out = n20_Out + 17.0;
	// Multiply #21
	float n21_Out = sg_Time * u_sgParams[3].x;
	// Floor #22
	float n22_Out = floor(n21_Out);
	// Combine #26
	vec4 n26_RGBA = vec4(n25_Out, n22_Out, 0.0, 1.0);
	// Value Noise #27
	float n27_Out = sgValueNoise(n26_RGBA.xy, 1.0);
	// One Minus #33
	float n33_Out = 1.0 - u_sgParams[4].x;
	// Combine #23
	vec4 n23_RGBA = vec4(n20_Out, n22_Out, 0.0, 1.0);
	// Value Noise #24
	float n24_Out = sgValueNoise(n23_RGBA.xy, 1.0);
	// Step #34
	float n34_Out = step(n33_Out, n24_Out);
	// Multiply #28
	float n28_Out = sg_Time * u_sgParams[6].x;
	// Floor #29
	float n29_Out = floor(n28_Out);
	// Combine #30
	vec4 n30_RGBA = vec4(n29_Out, 5.0, 0.0, 1.0);
	// Value Noise #31
	float n31_Out = sgValueNoise(n30_RGBA.xy, 1.0);
	// Step #32
	float n32_Out = step(0.449999988, n31_Out);
	// Multiply #35
	float n35_Out = n34_Out * n32_Out;
	// Split #44
	vec2 n44_In = sg_UV0;
	// Multiply #45
	float n45_Out = n44_In.x * 2.0;
	// Multiply #46
	float n46_Out = sg_Time * 0.150000006;
	// Add #47
	float n47_Out = n45_Out + n46_Out;
	// Hue #48
	vec3 n48_Out = sgHueShift(vec3(1.0, 0.119999997, 0.0799999982), n47_Out);
	// DDX #52
	vec3 n52_Out = dFdx(sg_PositionWorld);
	// DDY #53
	vec3 n53_Out = dFdy(sg_PositionWorld);
	// Cross Product #54
	vec3 n54_Out = cross(n52_Out, n53_Out);
	// Normalize #55
	vec3 n55_Out = normalize(n54_Out);
	// Dot Product #57
	float n57_Out = dot(n55_Out, sg_ViewDirectionWorld);
	// Sign #58
	float n58_Out = sign(n57_Out);
	// Multiply #59
	vec3 n59_Out = n55_Out * vec3_splat(n58_Out);
	// Lerp #49
	vec3 n49_Out = mix(u_sgParams[7].xyz, u_sgParams[8].xyz, vec3_splat(n27_Out));
	// Multiply #50
	vec3 n50_Out = n49_Out * vec3_splat(n35_Out);
	// Fresnel Effect #60
	float n60_Out = pow(1.0 - clamp(dot(sgSafeNormalize(n59_Out), sgSafeNormalize(sg_ViewDirectionWorld)), 0.0, 1.0), 4.0);
	// Multiply #61
	float n61_Out = n60_Out * 1.5;
	// Multiply #62
	vec3 n62_Out = n48_Out * vec3_splat(n61_Out);
	// Add #63
	vec3 n63_Out = n50_Out + n62_Out;
	// Multiply #64
	vec3 n64_Out = n48_Out * vec3(0.150000006, 0.150000006, 0.150000006);
	// Add #65
	vec3 n65_Out = n63_Out + n64_Out;
	// Outputs
	vec3 sgOut_BaseColor = n48_Out;
	vec3 sgOut_Normal = n59_Out;
	float sgOut_Metallic = 0.5;
	float sgOut_Roughness = 0.25;
	vec3 sgOut_Emission = n65_Out;
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
