$input v_texcoord0

// Generated from Assets/ShaderGraphs/LaunchNight/NightShift.shadergraph by the shader graph compiler: edit the graph, not this file.
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
// u_sgParams[0]: Grain (Float)
// u_sgParams[1]: Fringe (Float)
// u_sgParams[2]: Alarm (Float)

void sgCustom_NightShift_8570(vec2 UV, float Time, out float Grain, out float Alarm)
{
float n = fract(sin(dot(floor(UV * vec2(960.0, 540.0)) + vec2_splat(fract(Time * 7.0) * 113.0), vec2(12.9898, 78.233))) * 43758.5453);
vec2 c = UV - vec2_splat(0.5);
float edge = smoothstep(0.25, 0.75, length(c * vec2(1.3, 1.0)));
float pulse = 0.5 + 0.5 * sin(Time * 4.4);
Grain = (n - 0.5);
Alarm = edge * pulse * pulse;
}


void main()
{
	vec4 sg_fragCoord = gl_FragCoord;
	vec2 sg_ScreenUV = v_texcoord0;
	vec2 sg_ScreenPixel = sg_fragCoord.xy;
	float sg_Time = u_time.y;
	float sg_DeltaTime = u_time.x;

	// Subtract #6
	vec2 n6_Out = sg_ScreenUV - vec2(0.5, 0.5);
	// Multiply #7
	vec2 n7_Out = n6_Out * vec2_splat(u_sgParams[1].x);
	// Add #8
	vec2 n8_Out = sg_ScreenUV + n7_Out;
	// Scene Color #9
	vec3 n9_Out = sgSceneColor(n8_Out);
	// Split #10
	vec3 n10_In = n9_Out;
	// Scene Color #11
	vec3 n11_Out = sgSceneColor(sg_ScreenUV);
	// Split #12
	vec3 n12_In = n11_Out;
	// Subtract #13
	vec2 n13_Out = sg_ScreenUV - n7_Out;
	// Scene Color #14
	vec3 n14_Out = sgSceneColor(n13_Out);
	// Split #15
	vec3 n15_In = n14_Out;
	// Combine #16
	vec4 n16_RGBA = vec4(n10_In.x, n12_In.y, n15_In.z, 1.0);
	// NightShift #18
	float n18_Grain;
	float n18_Alarm;
	sgCustom_NightShift_8570(sg_ScreenUV, sg_Time, n18_Grain, n18_Alarm);
	// Multiply #21
	float n21_Out = n18_Grain * u_sgParams[0].x;
	// Add #22
	vec3 n22_Out = n16_RGBA.xyz + vec3_splat(n21_Out);
	// Multiply #19
	float n19_Out = n18_Alarm * u_sgParams[2].x;
	// Multiply #20
	vec3 n20_Out = vec3_splat(n19_Out) * vec3(1.0, 0.0500000007, 0.0199999996);
	// Add #23
	vec3 n23_Out = n22_Out + n20_Out;
	// Outputs
	vec3 sgOut_Color = n23_Out;

	gl_FragColor = vec4(sgOut_Color, 1.0);
}
