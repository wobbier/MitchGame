$input v_texcoord0

// Generated from Assets/ShaderGraphs/Mandelbrot.shadergraph by the shader graph compiler: edit the graph, not this file.
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
// u_sgParams[0]: Center (Vector 2)
// u_sgParams[1]: Zoom (Float)
// u_sgParams[2]: Iterations (Float)
// u_sgParams[3]: Palette Phase (Float)
// u_sgParams[4]: Palette Cycles (Float)
// u_sgParams[5]: Contour Density (Float)
// u_sgParams[6]: Glow (Float)
// u_sgParams[7]: Brightness (Float)
// u_sgParams[8]: Zoom Speed (Float)

void sgCustom_ScalePeriodicCoordinates_7526(vec2 UV, vec2 Center, float Zoom, float Time, float ZoomSpeed, out vec2 C, out float PixelSize, out vec2 NextC, out float NextPixelSize, out float Blend, out float Active, out float NextActive, out float MuBias, out float NextMuBias, out float ViewAngle, out float NextViewAngle, out float LoopPhase, out float CoreFade)
{
// The selected critical orbit lands on a repelling fixed point.
// Three iterations scale local detail by |lambda^3| and rotate it by arg(lambda^3).
// Repeat a smooth log-radius tile. Time only translates this fixed field;
// there is no camera reset, screen-space transition or layer handoff.
float loopStops = 1.228841185211;
float loopAngle = -0.023399272963;
float dx = max(abs(dFdx(UV.x)), 0.000001);
float dy = max(abs(dFdy(UV.y)), 0.000001);
float aspect = dy / dx;
vec2 plane = vec2((UV.x - 0.5) * aspect, 0.5 - UV.y) * max(2.7, 3.6 / aspect);
float screenPixel = dy * max(2.7, 3.6 / aspect);
float baseZoom = clamp(Zoom, 0.25, 12000.0);
float speed = clamp(ZoomSpeed, 0.0, 1.0);
float period = loopStops / max(speed, 0.0001);
LoopPhase = speed > 0.0 ? fract(max(Time, 0.0) / period) : 0.0;
float radius = max(length(plane), screenPixel * 0.25);
vec2 direction = plane / radius;
float tile = fract(log2(radius / 0.25) / loopStops - LoopPhase);
float scaleA = 0.25 * exp2(tile * loopStops) / baseZoom;
float scaleB = scaleA * 0.4266600140686584;
ViewAngle = tile * loopAngle;
NextViewAngle = (tile - 1.0) * loopAngle;
float ca = cos(ViewAngle);
float sa = sin(ViewAngle);
float cb = cos(NextViewAngle);
float sb = sin(NextViewAngle);
C = Center + vec2(ca * direction.x - sa * direction.y, sa * direction.x + ca * direction.y) * scaleA;
NextC = Center + vec2(cb * direction.x - sb * direction.y, sb * direction.x + cb * direction.y) * scaleB;
// Include the radial shear's largest singular value in the pixel footprint.
PixelSize = max(screenPixel * scaleA / radius * 1.015, 0.00000001);
NextPixelSize = max(screenPixel * scaleB / radius * 1.015, 0.00000001);
// At either edge the surviving sample has exactly the same complex
// coordinate, orientation and potential bias. Values and slopes join.
Blend = smoothstep(0.15, 0.85, tile);
MuBias = tile * 3.0;
NextMuBias = (tile - 1.0) * 3.0;
CoreFade = smoothstep(screenPixel * 0.5, screenPixel * 2.5, radius);
if (speed <= 0.0)
{
    C = Center + plane / baseZoom;
    NextC = C;
    PixelSize = max(screenPixel / baseZoom, 0.00000001);
    NextPixelSize = PixelSize;
    Blend = 0.0;
    MuBias = 0.0;
    NextMuBias = 0.0;
    ViewAngle = 0.0;
    NextViewAngle = 0.0;
    CoreFade = 1.0;
}
Active = 1.0 - Blend;
NextActive = Blend;
}

void sgCustom_MandelbrotDistance_29431(vec2 C, float Iterations, float Active, float PixelSize, float ViewAngle, out vec4 Field)
{
// Skip samples outside the fixed spatial tile overlap.
Field = vec4(0.0, 0.0, 0.0, 0.0);
if (Active <= 0.0) return;
// Analytic rejection of the main cardioid and period-two bulb.
float cy2 = C.y * C.y;
float cx = C.x - 0.25;
float q = cx * cx + cy2;
if (q * (q + cx) < 0.25 * cy2 || (C.x + 1.0) * (C.x + 1.0) + cy2 < 0.0625)
{
    return;
}
vec2 z = vec2(0.0, 0.0);
vec2 dz = vec2(0.0, 0.0);
float limit = floor(clamp(Iterations, 32.0, 512.0));
for (int i = 0; i < 512; ++i)
{
    if (float(i) >= limit) break;
    dz = 2.0 * vec2(z.x * dz.x - z.y * dz.y, z.x * dz.y + z.y * dz.x) + vec2(1.0, 0.0);
    z = vec2(z.x * z.x - z.y * z.y, 2.0 * z.x * z.y) + C;
    float r2 = dot(z, z);
    if (r2 > 256.0)
    {
        // Continuous potential removes escape-count banding. dz/dc gives an
        // exterior distance estimate and a normal for the engraved relief.
        float mu = float(i) + 1.0 - log2(0.5 * log2(r2));
        float distance = 0.5 * log(r2) * sqrt(r2) / max(length(dz), 0.000001);
        vec2 normal = vec2(z.x * dz.x + z.y * dz.y, z.y * dz.x - z.x * dz.y);
        normal /= max(length(normal), 0.000001);
        // Rotate the gradient into the view so repeated levels share lighting.
        float ca = cos(ViewAngle);
        float sa = sin(ViewAngle);
        normal = vec2(ca * normal.x + sa * normal.y, -sa * normal.x + ca * normal.y);
        float light = 0.5 + 0.5 * dot(normal, vec2(-0.6, 0.8));
        // Features narrower than a pixel receive fractional coverage,
        // preventing isolated escape samples from flashing at full brightness.
        float coverage = 0.5 + 0.5 * smoothstep(0.0, max(PixelSize, 0.00000001) * 0.8, distance);
        Field = vec4(mu, distance, light, coverage);
        break;
    }
}
}

void sgCustom_GildedContours_315(vec4 Field, float PixelSize, float LoopPhase, float PalettePhase, float PaletteCycles, float ContourDensity, float Glow, float Brightness, float MuBias, float CoreFade, out vec3 Color)
{
float mu = Field.x + MuBias;
float phase = mu * clamp(ContourDensity, 0.005, 0.15) + PalettePhase + LoopPhase * floor(clamp(PaletteCycles, 0.0, 4.0) + 0.5);
// The distance estimate gives |gradient(mu)| = 1 / (ln(2) * distance).
// This stays stable through the escape loop and repeated scales.
float footprint = 1.442695 * PixelSize / max(Field.y, PixelSize * 0.01);
float paletteWidth = 6.2831853 * clamp(ContourDensity, 0.005, 0.15) * footprint;
float wave = 0.5 + 0.5 * cos(6.2831853 * phase) * exp2(-0.06 * paletteWidth * paletteWidth);
vec3 ink = vec3(0.004, 0.012, 0.035);
vec3 teal = vec3(0.015, 0.46, 0.58);
vec3 gold = vec3(1.2, 0.48, 0.075);
vec3 pearl = vec3(1.55, 1.25, 0.72);
vec3 palette = mix(ink, teal, smoothstep(0.04, 0.5, wave));
palette = mix(palette, gold, smoothstep(0.5, 0.82, wave));
palette = mix(palette, pearl, smoothstep(0.86, 1.0, wave));
// Filter contour bands and relief when their details become subpixel.
float bands = 0.88 + 0.12 * cos(2.4 * mu) * exp2(-footprint * footprint);
float relief = 0.48 + 0.72 * mix(0.5, Field.z, exp2(-0.05 * footprint * footprint));
float edge = exp(-sqrt(max(Field.y, 0.0) / max(PixelSize, 0.00000001)) * 0.7);
float atmosphere = exp(-sqrt(max(Field.y, 0.0) / max(PixelSize, 0.00000001)) * 0.085);
vec3 exterior = mix(ink * 0.35, palette * bands * relief, atmosphere);
exterior += vec3(0.05, 0.52, 0.7) * edge * clamp(Glow, 0.0, 3.0);
// The unescaped set stays velvet-dark, including points at the iteration cap.
vec3 interior = vec3(0.0015, 0.003, 0.009);
Color = mix(interior, exterior, Field.w) * clamp(Brightness, 0.0, 4.0) * CoreFade;
}


void main()
{
	vec4 sg_fragCoord = gl_FragCoord;
	vec2 sg_UV0 = v_texcoord0;
	float sg_Time = u_time.y;
	float sg_DeltaTime = u_time.x;

	// Scale Periodic Coordinates #3
	vec2 n3_C;
	float n3_PixelSize;
	vec2 n3_NextC;
	float n3_NextPixelSize;
	float n3_Blend;
	float n3_Active;
	float n3_NextActive;
	float n3_MuBias;
	float n3_NextMuBias;
	float n3_ViewAngle;
	float n3_NextViewAngle;
	float n3_LoopPhase;
	float n3_CoreFade;
	sgCustom_ScalePeriodicCoordinates_7526(sg_UV0, u_sgParams[0].xy, u_sgParams[1].x, sg_Time, u_sgParams[8].x, n3_C, n3_PixelSize, n3_NextC, n3_NextPixelSize, n3_Blend, n3_Active, n3_NextActive, n3_MuBias, n3_NextMuBias, n3_ViewAngle, n3_NextViewAngle, n3_LoopPhase, n3_CoreFade);
	// Mandelbrot Distance #4
	vec4 n4_Field;
	sgCustom_MandelbrotDistance_29431(n3_C, u_sgParams[2].x, n3_Active, n3_PixelSize, n3_ViewAngle, n4_Field);
	// Gilded Contours #5
	vec3 n5_Color;
	sgCustom_GildedContours_315(n4_Field, n3_PixelSize, n3_LoopPhase, u_sgParams[3].x, u_sgParams[4].x, u_sgParams[5].x, u_sgParams[6].x, u_sgParams[7].x, n3_MuBias, n3_CoreFade, n5_Color);
	// Mandelbrot Distance #21
	vec4 n21_Field;
	sgCustom_MandelbrotDistance_29431(n3_NextC, u_sgParams[2].x, n3_NextActive, n3_NextPixelSize, n3_NextViewAngle, n21_Field);
	// Gilded Contours #22
	vec3 n22_Color;
	sgCustom_GildedContours_315(n21_Field, n3_NextPixelSize, n3_LoopPhase, u_sgParams[3].x, u_sgParams[4].x, u_sgParams[5].x, u_sgParams[6].x, u_sgParams[7].x, n3_NextMuBias, n3_CoreFade, n22_Color);
	// Lerp #23
	vec3 n23_Out = mix(n5_Color, n22_Color, vec3_splat(n3_Blend));
	// Outputs
	vec3 sgOut_Color = n23_Out;

	gl_FragColor = vec4(sgOut_Color, 1.0);
}
