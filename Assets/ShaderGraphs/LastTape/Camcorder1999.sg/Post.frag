$input v_texcoord0

// Generated from Assets/ShaderGraphs/LastTape/Camcorder1999.shadergraph by the shader graph compiler: edit the graph, not this file.
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
SAMPLER2D(s_sgTex0, 0); // Assets/Textures/LastTape/CameraFont.png
// u_sgParams[0]: Tape Wear (Float)
// u_sgParams[1]: Sensor Grain (Float)
// u_sgParams[2]: Chroma Bleed (Float)
// u_sgParams[3]: 4:3 Frame (Float)
// u_sgParams[4]: Camera OSD (Float)
// u_sgParams[5]: Lens Vignette (Float)

void sgCustom_TapeTransport_22737(vec2 UV, float Clock, float Wear, float Bleed, out vec2 Center, out vec2 Red, out vec2 Blue, out vec2 Soft)
{
// 480-line capture, mild lens bow and horizontal transport instability.
float frame = floor(Clock * 29.97);
float row = floor(UV.y * 480.0);
float rowNoise = fract(sin(row * 12.9898 + frame * 4.1414) * 43758.5453) - 0.5;
float tracking = smoothstep(0.972, 0.998, UV.y);
float splice = step(0.987, fract(Clock * 0.071));
vec2 p = UV - vec2_splat(0.5);
vec2 warped = UV + p * dot(p,p) * 0.032 * Wear;
warped.x += Wear * (rowNoise * 0.00065 + sin(Clock*1.7) * 0.00018
             + tracking * rowNoise * 0.006 + splice * sin(row*.14) * 0.002);
float aspect = u_viewRect.z / max(u_viewRect.w, 1.0);
vec2 raster = vec2(480.0 * aspect, 480.0);
vec2 lowRes = (floor(warped * raster) + vec2_splat(0.5)) / raster;
Center = mix(UV, lowRes, Wear * 0.78);
Red = Center + vec2(Bleed * Wear / raster.x, 0.0);
Blue = Center - vec2(Bleed * Wear * 0.65 / raster.x, 0.0);
Soft = Center + vec2(3.5 * Wear / raster.x, 0.0);
}

void sgCustom_Hi8Signal_89969(vec3 Center, vec3 Red, vec3 Blue, vec3 Soft, vec2 UV, float Clock, float Wear, float Grain, float Vignette, out vec3 Color)
{
vec3 signal = vec3(Red.r, Center.g, Blue.b);
float luma = dot(signal, vec3(0.299, 0.587, 0.114));
float softLuma = dot(Soft, vec3(0.299, 0.587, 0.114));
vec3 chroma = Soft - vec3_splat(softLuma);
signal = mix(signal, vec3_splat(luma) + chroma * 0.78, Wear * 0.32);
// A consumer CCD: soft highlight knee, lifted blacks and a green/cyan bias.
signal = pow(max(signal, vec3_splat(0.0)), vec3_splat(0.96));
signal = signal * vec3(0.98, 1.01, 1.025) + vec3(0.008, 0.012, 0.014) * Wear;
float frame = floor(Clock * 29.97);
vec2 pixel = floor(UV * vec2(640.0,480.0));
float noise = fract(sin(dot(pixel,vec2(12.9898,78.233)) + frame*3.119) * 43758.5453) - 0.5;
float chromaNoise = fract(sin(dot(pixel,vec2(39.346,11.135)) + frame*1.719) * 47453.5453) - 0.5;
signal += (vec3_splat(noise) + vec3(chromaNoise,0.0,-chromaNoise)*0.25) * Grain * (1.4-luma*.65) * Wear;
float scan = sin(UV.y*480.0*3.14159265 + mod(frame,2.0)*3.14159265);
signal *= 1.0 - (0.014 + scan*0.009) * Wear;
vec2 p = (UV - vec2_splat(0.5)) * vec2(1.12,1.0);
signal *= 1.0 - smoothstep(0.18,0.72,length(p)) * Vignette;
// A narrow head-switching band, kept below the picture and away from faces.
float tracking = smoothstep(0.976,0.999,UV.y);
signal = mix(signal, vec3_splat(0.10+noise*.16), tracking*Wear*.32);
Color = clamp(signal,vec3_splat(0.0),vec3_splat(1.0));
}

void sgCustom_CameraDisplay_73719(vec2 UV, float Clock, float Frame, out vec2 GlyphUV, out float Active, out float FrameMask, out float Dot, out float Battery)
{
float aspect = u_viewRect.z / max(u_viewRect.w,1.0);
vec2 fit = vec2(max(1.0,aspect/(4.0/3.0)),max(1.0,(4.0/3.0)/aspect));
vec2 frameUV = (UV - vec2_splat(0.5)) * mix(vec2_splat(1.0),fit,Frame) + vec2_splat(0.5);
FrameMask = step(0.0,frameUV.x)*step(frameUV.x,1.0)*step(0.0,frameUV.y)*step(frameUV.y,1.0);
vec2 pixel = floor(frameUV * vec2(640.0,480.0));
float glyph = 32.0;
float inkActive = 0.0;
vec2 local = vec2_splat(0.0);
vec2 line0 = (pixel - vec2(38.0, 30.0)) / 2.0;
if (line0.x >= 0.0 && line0.x < 18.0 && line0.y >= 0.0 && line0.y < 7.0)
{
    float index = floor(line0.x / 6.0);
    local = vec2(mod(floor(line0.x),6.0),floor(line0.y));
    inkActive = 1.0;
    if (index == 0.0) glyph = 82.0;
    if (index == 1.0) glyph = 69.0;
    if (index == 2.0) glyph = 67.0;
}
vec2 line1 = (pixel - vec2(513.0, 30.0)) / 2.0;
if (line1.x >= 0.0 && line1.x < 12.0 && line1.y >= 0.0 && line1.y < 7.0)
{
    float index = floor(line1.x / 6.0);
    local = vec2(mod(floor(line1.x),6.0),floor(line1.y));
    inkActive = 1.0;
    if (index == 0.0) glyph = 83.0;
    if (index == 1.0) glyph = 80.0;
}
vec2 line2 = (pixel - vec2(38.0, 422.0)) / 2.0;
if (line2.x >= 0.0 && line2.x < 66.0 && line2.y >= 0.0 && line2.y < 7.0)
{
    float index = floor(line2.x / 6.0);
    local = vec2(mod(floor(line2.x),6.0),floor(line2.y));
    inkActive = 1.0;
    if (index == 0.0) glyph = 49.0;
    if (index == 1.0) glyph = 49.0;
    if (index == 2.0) glyph = 58.0;
    if (index == 3.0) glyph = 53.0;
    if (index == 4.0) glyph = 56.0;
    if (index == 5.0) glyph = 58.0;
    if (index == 6.0) glyph = 48.0 + floor(mod(Clock,60.0)/10.0);
    if (index == 7.0) glyph = 48.0 + floor(mod(Clock,10.0));
    if (index == 8.0) glyph = 32.0;
    if (index == 9.0) glyph = 80.0;
    if (index == 10.0) glyph = 77.0;
}
vec2 line3 = (pixel - vec2(38.0, 446.0)) / 2.0;
if (line3.x >= 0.0 && line3.x < 72.0 && line3.y >= 0.0 && line3.y < 7.0)
{
    float index = floor(line3.x / 6.0);
    local = vec2(mod(floor(line3.x),6.0),floor(line3.y));
    inkActive = 1.0;
    if (index == 0.0) glyph = 74.0;
    if (index == 1.0) glyph = 85.0;
    if (index == 2.0) glyph = 76.0;
    if (index == 3.0) glyph = 46.0;
    if (index == 4.0) glyph = 32.0;
    if (index == 5.0) glyph = 48.0;
    if (index == 6.0) glyph = 51.0;
    if (index == 7.0) glyph = 32.0;
    if (index == 8.0) glyph = 49.0;
    if (index == 9.0) glyph = 57.0;
    if (index == 10.0) glyph = 57.0;
    if (index == 11.0) glyph = 57.0;
}
vec2 line4 = (pixel - vec2(490.0, 446.0)) / 2.0;
if (line4.x >= 0.0 && line4.x < 48.0 && line4.y >= 0.0 && line4.y < 7.0)
{
    float index = floor(line4.x / 6.0);
    local = vec2(mod(floor(line4.x),6.0),floor(line4.y));
    inkActive = 1.0;
    if (index == 0.0) glyph = 72.0;
    if (index == 1.0) glyph = 73.0;
    if (index == 2.0) glyph = 56.0;
    if (index == 3.0) glyph = 32.0;
    if (index == 4.0) glyph = 47.0;
    if (index == 5.0) glyph = 32.0;
    if (index == 6.0) glyph = 48.0;
    if (index == 7.0) glyph = 49.0;
}
GlyphUV = (vec2(mod(glyph,16.0)*6.0, floor(glyph/16.0)*8.0) + local + vec2_splat(0.5)) / vec2(96.0,64.0);
Active = inkActive;
Dot = step(length(pixel-vec2(25.0,36.0)),4.0) * step(0.18,fract(Clock*.8));
vec2 b = abs(pixel-vec2(581.0,36.0));
float outer = step(b.x,20.0)*step(b.y,8.0);
float inner = step(b.x,18.0)*step(b.y,6.0);
float fill = step(pixel.x,584.0)*step(b.x,15.0)*step(b.y,4.0);
Battery = max(outer-inner,fill);
Battery = max(Battery,step(abs(pixel.x-604.0),2.0)*step(b.y,3.0));
}

void sgCustom_RecordToTape_18091(vec3 Image, float Glyph, float Active, float Mask, float Dot, float Battery, float OSD, out vec3 Color)
{
float white = max(Glyph*Active,Battery)*OSD;
vec3 image = mix(Image,vec3(0.91,0.96,0.93),white*.9);
image = mix(image,vec3(0.94,0.13,0.08),Dot*OSD);
Color = image * Mask;
}


void main()
{
	vec4 sg_fragCoord = gl_FragCoord;
	vec2 sg_UV0 = v_texcoord0;
	float sg_Time = u_time.y;
	float sg_DeltaTime = u_time.x;

	// TapeTransport #10
	vec2 n10_Center;
	vec2 n10_Red;
	vec2 n10_Blue;
	vec2 n10_Soft;
	sgCustom_TapeTransport_22737(sg_UV0, sg_Time, u_sgParams[0].x, u_sgParams[2].x, n10_Center, n10_Red, n10_Blue, n10_Soft);
	// Scene Color #11
	vec3 n11_Out = sgSceneColor(n10_Center);
	// Scene Color #12
	vec3 n12_Out = sgSceneColor(n10_Red);
	// Scene Color #13
	vec3 n13_Out = sgSceneColor(n10_Blue);
	// Scene Color #14
	vec3 n14_Out = sgSceneColor(n10_Soft);
	// Hi8Signal #15
	vec3 n15_Color;
	sgCustom_Hi8Signal_89969(n11_Out, n12_Out, n13_Out, n14_Out, sg_UV0, sg_Time, u_sgParams[0].x, u_sgParams[1].x, u_sgParams[5].x, n15_Color);
	// CameraDisplay #16
	vec2 n16_GlyphUV;
	float n16_Active;
	float n16_FrameMask;
	float n16_Dot;
	float n16_Battery;
	sgCustom_CameraDisplay_73719(sg_UV0, sg_Time, u_sgParams[3].x, n16_GlyphUV, n16_Active, n16_FrameMask, n16_Dot, n16_Battery);
	// Sample Texture 2D (Data) #18
	vec4 n18_RGBA = texture2D(s_sgTex0, n16_GlyphUV);
	// RecordToTape #19
	vec3 n19_Color;
	sgCustom_RecordToTape_18091(n15_Color, n18_RGBA.x, n16_Active, n16_FrameMask, n16_Dot, n16_Battery, u_sgParams[4].x, n19_Color);
	// Outputs
	vec3 sgOut_Color = n19_Color;

	gl_FragColor = vec4(sgOut_Color, 1.0);
}
