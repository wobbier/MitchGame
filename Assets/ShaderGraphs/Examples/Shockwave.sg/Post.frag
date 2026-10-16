$input v_texcoord0

// Generated from Assets/ShaderGraphs/Examples/Shockwave.shadergraph by the shader graph compiler: edit the graph, not this file.
// A full-screen pass (with the engine's Post/Fullscreen.vert) on the HDR scene before tonemapping,
// or on the display image after it (the graph's Injection setting).
#define SG_TARGET_POST 1

#include "Common.sh"
#include "ShaderGraph/SGLib.sh"

SAMPLER2D(s_sgSceneColor, 6);
SAMPLER2D(s_sgSceneDepth, 7);
uniform vec4 u_sgPostProjection;   // x P[2][2], y P[3][2], z 1 = orthographic, w 1 = depth range -1..1
uniform vec4 u_sgPostProjection2;  // x P[0][0], y P[1][1], z far distance (sky)
uniform mat4 u_sgPostInvView;      // the camera's view -> world (full-screen views are orthographic)

vec3 sgSceneColor(vec2 _uv)
{
	return texture2DLod(s_sgSceneColor, _uv, 0.0).rgb;
}

// Linear view depth (distance along the view) of the opaque scene under a screen UV.
float sgSceneDepth(vec2 _uv)
{
	float raw = texture2DLod(s_sgSceneDepth, _uv, 0.0).r;
	if (raw >= 0.99999)
	{
		return u_sgPostProjection2.z;
	}
	float ndc = u_sgPostProjection.w > 0.5 ? raw * 2.0 - 1.0 : raw;
	if (u_sgPostProjection.z > 0.5)
	{
		return (ndc - u_sgPostProjection.y) / u_sgPostProjection.x;
	}
	return u_sgPostProjection.y / (ndc - u_sgPostProjection.x);
}

// The view-space position of the scene under a screen UV (top-left origin).
vec3 sgViewPosition(vec2 _uv)
{
	vec2 ndc = vec2(_uv.x * 2.0 - 1.0, 1.0 - _uv.y * 2.0);
	vec2 scale = vec2(1.0 / u_sgPostProjection2.x, 1.0 / u_sgPostProjection2.y);
	float viewZ = sgSceneDepth(_uv);
	return u_sgPostProjection.z > 0.5 ? vec3(ndc * scale, viewZ) : vec3(ndc * scale * viewZ, viewZ);
}

// The scene's view-space normal, from one-pixel depth taps on the flatter side of each axis.
vec3 sgViewNormal(vec2 _uv)
{
	vec3 center = sgViewPosition(_uv);
	vec2 dx = vec2(u_viewTexel.x, 0.0);
	vec2 dy = vec2(0.0, u_viewTexel.y);
	vec3 left = sgViewPosition(_uv - dx);
	vec3 right = sgViewPosition(_uv + dx);
	vec3 up = sgViewPosition(_uv - dy);
	vec3 down = sgViewPosition(_uv + dy);
	vec3 stepX = abs(right.z - center.z) < abs(center.z - left.z) ? right - center : center - left;
	vec3 stepY = abs(down.z - center.z) < abs(center.z - up.z) ? down - center : center - up;
	vec3 normal = sgSafeNormalize(cross(stepX, stepY));
	return dot(normal, center) > 0.0 ? -normal : normal;
}

uniform vec4 u_sgParams[16];
// u_sgParams[0]: Period (Float)
// u_sgParams[1]: Strength (Float)
// u_sgParams[2]: Width (Float)
// u_sgParams[3]: Center (Vector 2)
// u_sgParams[4]: Flash Color (Vector 3)
// u_sgParams[5]: Fringe (Float)


void main()
{
	vec4 sg_fragCoord = gl_FragCoord;
	vec2 sg_UV0 = v_texcoord0;
	vec2 sg_ScreenUV = v_texcoord0;
	vec2 sg_ScreenPixel = sg_fragCoord.xy;
	float sg_Time = u_time.y;
	float sg_DeltaTime = u_time.x;

	// Subtract #9
	vec2 n9_Out = sg_UV0 - u_sgParams[3].xy;
	// Normalize #34
	vec2 n34_Out = normalize(n9_Out);
	// Divide #11
	vec2 n11_Out = sg_ScreenPixel / sg_ScreenUV;
	// Split #12
	vec2 n12_In = n11_Out;
	// Divide #13
	float n13_Out = n12_In.x / n12_In.y;
	// Combine #14
	vec4 n14_RGBA = vec4(n13_Out, 1.0, 0.0, 1.0);
	// Multiply #15
	vec2 n15_Out = n9_Out * n14_RGBA.xy;
	// Length #16
	float n16_Out = length(n15_Out);
	// Divide #18
	float n18_Out = sg_Time / u_sgParams[0].x;
	// Fraction #19
	float n19_Out = fract(n18_Out);
	// One Minus #20
	float n20_Out = 1.0 - n19_Out;
	// Square #21
	float n21_Out = n20_Out * n20_Out;
	// One Minus #22
	float n22_Out = 1.0 - n21_Out;
	// Multiply #23
	float n23_Out = n22_Out * 1.25;
	// Subtract #26
	float n26_Out = n16_Out - n23_Out;
	// Divide #27
	float n27_Out = n26_Out / u_sgParams[2].x;
	// Absolute #28
	float n28_Out = abs(n27_Out);
	// Saturate #29
	float n29_Out = clamp(n28_Out, 0.0, 1.0);
	// One Minus #30
	float n30_Out = 1.0 - n29_Out;
	// Smoothstep #31
	float n31_Out = smoothstep(0.0, 1.0, n30_Out);
	// Multiply #32
	float n32_Out = n31_Out * n21_Out;
	// Multiply #33
	float n33_Out = n32_Out * u_sgParams[1].x;
	// Multiply #35
	vec2 n35_Out = n34_Out * vec2_splat(n33_Out);
	// Subtract #38
	vec2 n38_Out = sg_UV0 - n35_Out;
	// Scene Color #39
	vec3 n39_Out = sgSceneColor(n38_Out);
	// Split #47
	vec3 n47_In = n39_Out;
	// Multiply #36
	float n36_Out = u_sgParams[5].x * 0.5;
	// Add #37
	float n37_Out = n36_Out + 1.0;
	// Multiply #40
	vec2 n40_Out = n35_Out * vec2_splat(n37_Out);
	// Subtract #41
	vec2 n41_Out = sg_UV0 - n40_Out;
	// Scene Color #42
	vec3 n42_Out = sgSceneColor(n41_Out);
	// Split #48
	vec3 n48_In = n42_Out;
	// Multiply #43
	float n43_Out = n37_Out * n37_Out;
	// Multiply #44
	vec2 n44_Out = n35_Out * vec2_splat(n43_Out);
	// Subtract #45
	vec2 n45_Out = sg_UV0 - n44_Out;
	// Scene Color #46
	vec3 n46_Out = sgSceneColor(n45_Out);
	// Split #49
	vec3 n49_In = n46_Out;
	// Combine #50
	vec4 n50_RGBA = vec4(n47_In.x, n48_In.y, n49_In.z, 1.0);
	// Negate #51
	float n51_Out = -n27_Out;
	// Saturate #52
	float n52_Out = clamp(n51_Out, 0.0, 1.0);
	// Multiply #53
	float n53_Out = n52_Out * n31_Out;
	// Multiply #54
	float n54_Out = n53_Out * n21_Out;
	// Multiply #55
	vec3 n55_Out = u_sgParams[4].xyz * vec3_splat(n54_Out);
	// Add #56
	vec3 n56_Out = n50_RGBA.xyz + n55_Out;
	// Outputs
	vec3 sgOut_Color = n56_Out;

	gl_FragColor = vec4(sgOut_Color, 1.0);
}
