$input v_texcoord0

// Generated from Assets/ShaderGraphs/Examples/WarpLens.shadergraph by the shader graph compiler: edit the graph, not this file.
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
// u_sgParams[0]: Strength (Float)
// u_sgParams[1]: Bulge (Float)
// u_sgParams[2]: Swirl (Float)
// u_sgParams[3]: Ghost (Float)
// u_sgParams[4]: Fringe (Float)


void main()
{
	vec4 sg_fragCoord = gl_FragCoord;
	vec2 sg_UV0 = v_texcoord0;
	float sg_Time = u_time.y;
	float sg_DeltaTime = u_time.x;

	// Multiply #10
	float n10_Out = sg_Time * 0.699999988;
	// Sine #11
	float n11_Out = sin(n10_Out);
	// Multiply #12
	float n12_Out = u_sgParams[2].x * u_sgParams[0].x;
	// Multiply #13
	float n13_Out = n11_Out * n12_Out;
	// Twirl #14
	vec2 n14_Out = sgTwirl(sg_UV0, vec2(0.5, 0.5), n13_Out, vec2(0.0, 0.0));
	// Multiply #15
	float n15_Out = u_sgParams[1].x * u_sgParams[0].x;
	// Spherize #16
	vec2 n16_Out = sgSpherize(n14_Out, vec2(0.5, 0.5), n15_Out, vec2(0.0, 0.0));
	// Subtract #9
	vec2 n9_Out = sg_UV0 - vec2(0.5, 0.5);
	// Length #17
	float n17_Out = length(n9_Out);
	// Square #18
	float n18_Out = n17_Out * n17_Out;
	// Multiply #19
	vec2 n19_Out = n9_Out * vec2_splat(n18_Out);
	// Multiply #20
	float n20_Out = u_sgParams[4].x * u_sgParams[0].x;
	// Multiply #21
	vec2 n21_Out = n19_Out * vec2_splat(n20_Out);
	// Add #22
	vec2 n22_Out = n16_Out + n21_Out;
	// Scene Color #23
	vec3 n23_Out = sgSceneColor(n22_Out);
	// Split #27
	vec3 n27_In = n23_Out;
	// Scene Color #24
	vec3 n24_Out = sgSceneColor(n16_Out);
	// Split #28
	vec3 n28_In = n24_Out;
	// Subtract #25
	vec2 n25_Out = n16_Out - n21_Out;
	// Scene Color #26
	vec3 n26_Out = sgSceneColor(n25_Out);
	// Split #29
	vec3 n29_In = n26_Out;
	// Combine #30
	vec4 n30_RGBA = vec4(n27_In.x, n28_In.y, n29_In.z, 1.0);
	// Multiply #31
	float n31_Out = sg_Time * 1.29999995;
	// Sine #32
	float n32_Out = sin(n31_Out);
	// Multiply #33
	float n33_Out = sg_Time * 0.899999976;
	// Cosine #34
	float n34_Out = cos(n33_Out);
	// Combine #35
	vec4 n35_RGBA = vec4(n32_Out, n34_Out, 0.0, 1.0);
	// Multiply #36
	float n36_Out = u_sgParams[0].x * 0.0199999996;
	// Multiply #37
	vec2 n37_Out = n35_RGBA.xy * vec2_splat(n36_Out);
	// Add #38
	vec2 n38_Out = n16_Out + n37_Out;
	// Scene Color #39
	vec3 n39_Out = sgSceneColor(n38_Out);
	// Saturate #40
	float n40_Out = clamp(u_sgParams[0].x, 0.0, 1.0);
	// Multiply #41
	float n41_Out = u_sgParams[3].x * n40_Out;
	// Lerp #42
	vec3 n42_Out = mix(n30_RGBA.xyz, n39_Out, vec3_splat(n41_Out));
	// Multiply #43
	float n43_Out = sg_Time * 0.449999988;
	// Sine #44
	float n44_Out = sin(n43_Out);
	// Multiply #45
	float n45_Out = u_sgParams[0].x * 0.0399999991;
	// Multiply #46
	float n46_Out = n44_Out * n45_Out;
	// Hue #47
	vec3 n47_Out = sgHueShift(n42_Out, n46_Out);
	// Smoothstep #49
	float n49_Out = smoothstep(0.25, 0.850000024, n17_Out);
	// One Minus #50
	float n50_Out = 1.0 - n49_Out;
	// Multiply #52
	float n52_Out = n40_Out * 0.800000012;
	// Lerp #53
	float n53_Out = mix(1.0, n50_Out, n52_Out);
	// Multiply #54
	vec3 n54_Out = n47_Out * vec3_splat(n53_Out);
	// Outputs
	vec3 sgOut_Color = n54_Out;

	gl_FragColor = vec4(sgOut_Color, 1.0);
}
