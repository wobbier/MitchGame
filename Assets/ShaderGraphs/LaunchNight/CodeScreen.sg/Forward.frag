$input v_worldPos, v_normal, v_tangent, v_bitangent, v_texcoord0, v_viewPos, v_objectPos, v_objectNormal

// Generated from Assets/ShaderGraphs/LaunchNight/CodeScreen.shadergraph by the shader graph compiler: edit the graph, not this file.

#include "Common.sh"
#include "StandardSurface.sh"
#include "ShaderGraph/SGLib.sh"

uniform vec4 u_sgParams[16];
// u_sgParams[0]: Scroll Speed (Float)
// u_sgParams[1]: Seed (Float)
// u_sgParams[2]: Brightness (Float)
// u_sgParams[3]: Background (Vector 3)
// u_sgParams[4]: UV Rect (Vector 4)
// u_sgParams[5]: Flip (Vector 2)

void sgCustom_CodeLines_44436(vec2 UV, float Time, float Speed, float Seed, out vec3 Color)
{
float rows = 26.0;
float yy = UV.y * rows + Time * Speed;
float row = floor(yy);
float fy = fract(yy);
float h = fract(sin(row * 12.9898 + Seed * 78.233) * 43758.5453);
float h2 = fract(sin(row * 39.346 + Seed * 11.135) * 24634.6345);
float cols = 70.0;
float indent = floor(h2 * 4.0) * 2.0;
float gutter = UV.x * cols;
float cx = gutter - 4.0 - indent;
float c = floor(cx);
float fx = fract(cx);
float len = floor(6.0 + h * 44.0);
float hc = fract(sin((c + row * 97.0) * 7.31 + Seed) * 9137.17);
float word = floor((c + floor(h * 7.0)) / 5.0);
float hw = fract(sin((word + row * 31.0) * 3.17 + Seed * 1.7) * 5131.7);
float blank = step(h, 0.1);
float ink = step(0.0, c) * step(c, len) * step(0.15, hc) * (1.0 - blank);
float glyph = step(0.2, fy) * step(fy, 0.76) * step(0.12, fx) * step(fx, 0.88);
vec3 col = vec3(0.82, 0.85, 0.9);
if (hw < 0.2) col = vec3(0.78, 0.45, 0.98);
else if (hw < 0.34) col = vec3(1.0, 0.62, 0.3);
else if (hw < 0.52) col = vec3(0.36, 0.68, 1.0);
if (h2 > 0.86) col = vec3(0.4, 0.75, 0.38);
float numbers = step(gutter, 2.6) * step(0.4, fract(sin(row * 3.3) * 91.7)) * glyph;
float cursor = step(abs(UV.y - 0.93), 0.016) * step(abs(UV.x - (0.06 + fract(Time * 0.37 + Seed) * 0.5)), 0.008) * step(0.5, fract(Time * 1.6));
Color = col * ink * glyph + vec3(0.25, 0.27, 0.32) * numbers + vec3(0.9, 0.9, 0.9) * cursor;
}


void main()
{
	vec4 sg_fragCoord = gl_FragCoord;
	bool sg_frontFacing = gl_FrontFacing;
	vec2 sg_UV0 = v_texcoord0;
	float sg_Time = u_time.y;
	float sg_DeltaTime = u_time.x;

	// Swizzle .xy #8
	vec2 n8_Out = (u_sgParams[4]).xy;
	// Subtract #11
	vec2 n11_Out = sg_UV0 - n8_Out;
	// Swizzle .zw #9
	vec2 n9_Out = (u_sgParams[4]).zw;
	// Subtract #12
	vec2 n12_Out = n9_Out - n8_Out;
	// Divide #13
	vec2 n13_Out = n11_Out / n12_Out;
	// Subtract #14
	vec2 n14_Out = vec2(1.0, 1.0) - n13_Out;
	// Lerp #15
	vec2 n15_Out = mix(n13_Out, n14_Out, u_sgParams[5].xy);
	// CodeLines #17
	vec3 n17_Color;
	sgCustom_CodeLines_44436(n15_Out, sg_Time, u_sgParams[0].x, u_sgParams[1].x, n17_Color);
	// Add #18
	vec3 n18_Out = n17_Color + u_sgParams[3].xyz;
	// Split #19
	vec2 n19_In = n15_Out;
	// Multiply #20
	float n20_Out = n19_In.y * 900.0;
	// Sine #21
	float n21_Out = sin(n20_Out);
	// Multiply #22
	float n22_Out = n21_Out * 0.119999997;
	// Add #23
	float n23_Out = 0.879999995 + n22_Out;
	// Subtract #24
	vec2 n24_Out = n15_Out - vec2(0.5, 0.5);
	// Length #25
	float n25_Out = length(n24_Out);
	// Remap #26
	float n26_Out = 1.0 + (n25_Out - 0.349999994) * (0.550000012 - 1.0) / (0.75 - 0.349999994);
	// Saturate #27
	float n27_Out = clamp(n26_Out, 0.0, 1.0);
	// Multiply #28
	float n28_Out = n23_Out * n27_Out;
	// Multiply #29
	vec3 n29_Out = n18_Out * vec3_splat(n28_Out);
	// Step #31
	float n31_Out = step(0.0, n19_In.x);
	// Step #32
	float n32_Out = step(n19_In.x, 1.0);
	// Multiply #33
	float n33_Out = n31_Out * n32_Out;
	// Step #34
	float n34_Out = step(0.0, n19_In.y);
	// Step #35
	float n35_Out = step(n19_In.y, 1.0);
	// Multiply #36
	float n36_Out = n34_Out * n35_Out;
	// Multiply #37
	float n37_Out = n33_Out * n36_Out;
	// Multiply #38
	float n38_Out = u_sgParams[2].x * n37_Out;
	// Multiply #39
	vec3 n39_Out = n29_Out * vec3_splat(n38_Out);
	// Outputs
	vec3 sgOut_BaseColor = vec3(0.00999999978, 0.00999999978, 0.0120000001);
	vec3 sgOut_Normal = vec3(0.0, 0.0, 1.0);
	float sgOut_Metallic = 0.0;
	float sgOut_Roughness = 0.300000012;
	vec3 sgOut_Emission = n39_Out;
	float sgOut_Occlusion = 0.119999997;
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
