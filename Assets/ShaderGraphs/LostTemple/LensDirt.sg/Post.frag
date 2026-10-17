$input v_texcoord0

// Generated from Assets/ShaderGraphs/LostTemple/LensDirt.shadergraph by the shader graph compiler: edit the graph, not this file.
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
SAMPLER2D(s_sgTex0, 0); // Lens Dirt
// u_sgParams[0]: Dirt Intensity (Float)
// u_sgParams[1]: Threshold (Float)
// u_sgParams[2]: Fringe (Float)
// u_sgParams[3]: Glow Focus (Float)

void sgCustom_BrightLight_31628(float Threshold, out vec3 Light, out vec2 Centre)
{
// Samples the frame on a coarse grid (sgSceneColor is the target's scene-colour lookup): the light
// above Threshold, its average colour and where on screen it sits. Fixed sample positions, so bright
// points never leave ghost copies.
vec3 sum = vec3_splat(0.0);
vec2 centre = vec2_splat(0.0);
float total = 0.0;
for (int y = 0; y < 4; y++)
{
    for (int x = 0; x < 6; x++)
    {
        vec2 uv = vec2((float(x) + 0.5) / 6.0, (float(y) + 0.5) / 4.0);
        vec3 c = sgSceneColor(uv);
        float l = max(dot(c, vec3(0.2126, 0.7152, 0.0722)) - Threshold, 0.0);
        sum += c * l;
        centre += uv * l;
        total += l;
    }
}
Light = sum / (24.0 * max(Threshold, 0.05));
Centre = total > 0.0001 ? centre / total : vec2_splat(0.5);
}


void main()
{
	vec4 sg_fragCoord = gl_FragCoord;
	vec2 sg_ScreenUV = v_texcoord0;
	vec2 sg_ScreenPixel = sg_fragCoord.xy;

	// Subtract #8
	vec2 n8_Out = sg_ScreenUV - vec2(0.5, 0.5);
	// Multiply #9
	vec2 n9_Out = n8_Out * vec2_splat(u_sgParams[2].x);
	// Add #10
	vec2 n10_Out = sg_ScreenUV + n9_Out;
	// Scene Color #11
	vec3 n11_Out = sgSceneColor(n10_Out);
	// Split #12
	vec3 n12_In = n11_Out;
	// Scene Color #16
	vec3 n16_Out = sgSceneColor(sg_ScreenUV);
	// Split #17
	vec3 n17_In = n16_Out;
	// Subtract #13
	vec2 n13_Out = sg_ScreenUV - n9_Out;
	// Scene Color #14
	vec3 n14_Out = sgSceneColor(n13_Out);
	// Split #15
	vec3 n15_In = n14_Out;
	// Combine #18
	vec4 n18_RGBA = vec4(n12_In.x, n17_In.y, n15_In.z, 1.0);
	// Sample Texture 2D #26
	vec4 n26_RGBA = toLinear(texture2D(s_sgTex0, sg_ScreenUV));
	// BrightLight #19
	vec3 n19_Light;
	vec2 n19_Centre;
	sgCustom_BrightLight_31628(u_sgParams[1].x, n19_Light, n19_Centre);
	// Subtract #20
	vec2 n20_Out = sg_ScreenUV - n19_Centre;
	// Multiply #21
	vec2 n21_Out = n20_Out * vec2(1.77999997, 1.0);
	// Dot Product #22
	float n22_Out = dot(n21_Out, n21_Out);
	// Multiply #23
	float n23_Out = n22_Out * u_sgParams[3].x;
	// Negate #24
	float n24_Out = -n23_Out;
	// Exponential #25
	float n25_Out = exp(n24_Out);
	// Add #27
	float n27_Out = n25_Out + 0.25;
	// Multiply #28
	float n28_Out = n27_Out * u_sgParams[0].x;
	// Multiply #29
	vec3 n29_Out = n19_Light * vec3_splat(n28_Out);
	// Multiply #30
	vec3 n30_Out = n26_RGBA.xyz * n29_Out;
	// Add #31
	vec3 n31_Out = n18_RGBA.xyz + n30_Out;
	// Outputs
	vec3 sgOut_Color = n31_Out;

	gl_FragColor = vec4(sgOut_Color, 1.0);
}
