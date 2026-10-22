// Generated from Assets/ShaderGraphs/LaunchNight/Whiteboard.shadergraph by the shader graph compiler: edit the graph, not this file.
// Pairs with the engine's Decal.vert: the graph supplies the decal's surface, DecalCommon.sh
// projects and lights it like Decal.frag.
#define SG_TARGET_DECAL 1

#include "Common.sh"

SAMPLER2D(s_sgSceneDepth, 7);
#define DECAL_SCENE_DEPTH s_sgSceneDepth
#include "DecalCommon.sh"
#include "ShaderGraph/SGLib.sh"

// Linear view depth of the opaque scene under a screen UV.
float sgSceneDepth(vec2 _uv)
{
	return sceneViewPosition(_uv).z;
}

uniform vec4 u_sgParams[16];

void sgCustom_Marker_19759(vec2 UV, out float Mask1, out float Mask2, out float Mask3)
{
Mask1 = 0.0;
Mask2 = 0.0;
Mask3 = 0.0;
{
    vec2 q = vec2((UV.x - 0.05) / 0.055394, (UV.y - 0.07) / 0.095);
    if (q.y >= 0.0 && q.y < 1.0 && q.x >= 0.0 && q.x < 10.0)
    {
        float ci = floor(q.x);
        float px = floor(fract(q.x) * 6.0);
        float py = floor(q.y * 7.0);
        float glo = 0.0;
        float ghi = 0.0;
        if (ci > -0.5 && ci < 0.5) { glo = 459838.0; ghi = 15888.0; }
        if (ci > 0.5 && ci < 1.5) { glo = 1033777.0; ghi = 17969.0; }
        if (ci > 1.5 && ci < 2.5) { glo = 135310.0; ghi = 14468.0; }
        if (ci > 2.5 && ci < 3.5) { glo = 509487.0; ghi = 1057.0; }
        if (ci > 4.5 && ci < 5.5) { glo = 135310.0; ghi = 14468.0; }
        if (ci > 5.5 && ci < 6.5) { glo = 135327.0; ghi = 4228.0; }
        if (ci > 6.5 && ci < 7.5) { glo = 135300.0; ghi = 4100.0; }
        if (ci > 7.5 && ci < 8.5) { glo = 135300.0; ghi = 4100.0; }
        if (ci > 8.5 && ci < 9.5) { glo = 135300.0; ghi = 4100.0; }
        float hit = 0.0;
        if (px < 5.0)

        {
            float b = py * 5.0 + px;
            float word = b < 20.0 ? glo : ghi;
            float shift = b < 20.0 ? b : b - 20.0;
            hit = mod(floor(word / exp2(shift)), 2.0);
        }
        
        Mask2 = max(Mask2, hit);
    }
}
{
    vec2 q = vec2((UV.x - 0.05) / 0.034985, (UV.y - 0.43) / 0.06);
    if (q.y >= 0.0 && q.y < 1.0 && q.x >= 0.0 && q.x < 14.0)
    {
        float ci = floor(q.x);
        float px = floor(fract(q.x) * 6.0);
        float py = floor(q.y * 7.0);
        float glo = 0.0;
        float ghi = 0.0;
        if (ci > -0.5 && ci < 0.5) { glo = 575023.0; ghi = 15921.0; }
        if (ci > 0.5 && ci < 1.5) { glo = 1033774.0; ghi = 17969.0; }
        if (ci > 1.5 && ci < 2.5) { glo = 141873.0; ghi = 4228.0; }
        if (ci > 2.5 && ci < 3.5) { glo = 459838.0; ghi = 15888.0; }
        if (ci > 4.5 && ci < 5.5) { glo = 575022.0; ghi = 14897.0; }
        if (ci > 5.5 && ci < 6.5) { glo = 492607.0; ghi = 1057.0; }
        if (ci > 7.5 && ci < 8.5) { glo = 34350.0; ghi = 14881.0; }
        if (ci > 8.5 && ci < 9.5) { glo = 509487.0; ghi = 17701.0; }
        if (ci > 9.5 && ci < 10.5) { glo = 575025.0; ghi = 14897.0; }
        if (ci > 10.5 && ci < 11.5) { glo = 708145.0; ghi = 17977.0; }
        if (ci > 11.5 && ci < 12.5) { glo = 34350.0; ghi = 14881.0; }
        if (ci > 12.5 && ci < 13.5) { glo = 1033777.0; ghi = 17969.0; }
        float hit = 0.0;
        if (px < 5.0)

        {
            float b = py * 5.0 + px;
            float word = b < 20.0 ? glo : ghi;
            float shift = b < 20.0 ? b : b - 20.0;
            hit = mod(floor(word / exp2(shift)), 2.0);
        }
        
        Mask1 = max(Mask1, hit);
    }
}
{
    vec2 q = vec2((UV.x - 0.67) / 0.034985, (UV.y - 0.08) / 0.06);
    if (q.y >= 0.0 && q.y < 1.0 && q.x >= 0.0 && q.x < 5.0)
    {
        float ci = floor(q.x);
        float px = floor(fract(q.x) * 6.0);
        float py = floor(q.y * 7.0);
        float glo = 0.0;
        float ghi = 0.0;
        if (ci > -0.5 && ci < 0.5) { glo = 509487.0; ghi = 15921.0; }
        if (ci > 0.5 && ci < 1.5) { glo = 575025.0; ghi = 14897.0; }
        if (ci > 1.5 && ci < 2.5) { glo = 951854.0; ghi = 31281.0; }
        if (ci > 2.5 && ci < 3.5) { glo = 459838.0; ghi = 15888.0; }
        if (ci > 3.5 && ci < 4.5) { glo = 6336.0; ghi = 198.0; }
        float hit = 0.0;
        if (px < 5.0)

        {
            float b = py * 5.0 + px;
            float word = b < 20.0 ? glo : ghi;
            float shift = b < 20.0 ? b : b - 20.0;
            hit = mod(floor(word / exp2(shift)), 2.0);
        }
        
        Mask2 = max(Mask2, hit);
    }
}
{
    vec2 q = vec2((UV.x - 0.67) / 0.06414, (UV.y - 0.17) / 0.11);
    if (q.y >= 0.0 && q.y < 1.0 && q.x >= 0.0 && q.x < 3.0)
    {
        float ci = floor(q.x);
        float px = floor(fract(q.x) * 6.0);
        float py = floor(q.y * 7.0);
        float glo = 0.0;
        float ghi = 0.0;
        if (ci > -0.5 && ci < 0.5) { glo = 476718.0; ghi = 14897.0; }
        if (ci > 0.5 && ci < 1.5) { glo = 305544.0; ghi = 8479.0; }
        if (ci > 1.5 && ci < 2.5) { glo = 139807.0; ghi = 2114.0; }
        float hit = 0.0;
        if (px < 5.0)

        {
            float b = py * 5.0 + px;
            float word = b < 20.0 ? glo : ghi;
            float shift = b < 20.0 ? b : b - 20.0;
            hit = mod(floor(word / exp2(shift)), 2.0);
        }
        
        Mask2 = max(Mask2, hit);
    }
}
{
    vec2 q = vec2((UV.x - 0.64) / 0.020408, (UV.y - 0.52) / 0.035);
    if (q.y >= 0.0 && q.y < 1.0 && q.x >= 0.0 && q.x < 12.0)
    {
        float ci = floor(q.x);
        float px = floor(fract(q.x) * 6.0);
        float py = floor(q.y * 7.0);
        float glo = 0.0;
        float ghi = 0.0;
        if (ci > -0.5 && ci < 0.5) { glo = 575023.0; ghi = 15921.0; }
        if (ci > 0.5 && ci < 1.5) { glo = 575022.0; ghi = 14897.0; }
        if (ci > 2.5 && ci < 3.5) { glo = 708145.0; ghi = 17977.0; }
        if (ci > 3.5 && ci < 4.5) { glo = 575022.0; ghi = 14897.0; }
        if (ci > 4.5 && ci < 5.5) { glo = 135327.0; ghi = 4228.0; }
        if (ci > 6.5 && ci < 7.5) { glo = 135327.0; ghi = 4228.0; }
        if (ci > 7.5 && ci < 8.5) { glo = 575022.0; ghi = 14897.0; }
        if (ci > 8.5 && ci < 9.5) { glo = 575025.0; ghi = 14897.0; }
        if (ci > 9.5 && ci < 10.5) { glo = 34350.0; ghi = 14881.0; }
        if (ci > 10.5 && ci < 11.5) { glo = 1033777.0; ghi = 17969.0; }
        float hit = 0.0;
        if (px < 5.0)

        {
            float b = py * 5.0 + px;
            float word = b < 20.0 ? glo : ghi;
            float shift = b < 20.0 ? b : b - 20.0;
            hit = mod(floor(word / exp2(shift)), 2.0);
        }
        
        Mask3 = max(Mask3, hit);
    }
}
{
    vec2 q = vec2((UV.x - 0.64) / 0.020408, (UV.y - 0.58) / 0.035);
    if (q.y >= 0.0 && q.y < 1.0 && q.x >= 0.0 && q.x < 16.0)
    {
        float ci = floor(q.x);
        float px = floor(fract(q.x) * 6.0);
        float py = floor(q.y * 7.0);
        float glo = 0.0;
        float ghi = 0.0;
        if (ci > -0.5 && ci < 0.5) { glo = 135327.0; ghi = 4228.0; }
        if (ci > 0.5 && ci < 1.5) { glo = 1033777.0; ghi = 17969.0; }
        if (ci > 1.5 && ci < 2.5) { glo = 492607.0; ghi = 31777.0; }
        if (ci > 3.5 && ci < 4.5) { glo = 509487.0; ghi = 15921.0; }
        if (ci > 4.5 && ci < 5.5) { glo = 575025.0; ghi = 14897.0; }
        if (ci > 5.5 && ci < 6.5) { glo = 135310.0; ghi = 14468.0; }
        if (ci > 6.5 && ci < 7.5) { glo = 33825.0; ghi = 31777.0; }
        if (ci > 7.5 && ci < 8.5) { glo = 575023.0; ghi = 15921.0; }
        if (ci > 9.5 && ci < 10.5) { glo = 459838.0; ghi = 15888.0; }
        if (ci > 10.5 && ci < 11.5) { glo = 492607.0; ghi = 31777.0; }
        if (ci > 11.5 && ci < 12.5) { glo = 509487.0; ghi = 17701.0; }
        if (ci > 12.5 && ci < 13.5) { glo = 575025.0; ghi = 4433.0; }
        if (ci > 13.5 && ci < 14.5) { glo = 492607.0; ghi = 31777.0; }
        if (ci > 14.5 && ci < 15.5) { glo = 509487.0; ghi = 17701.0; }
        float hit = 0.0;
        if (px < 5.0)

        {
            float b = py * 5.0 + px;
            float word = b < 20.0 ? glo : ghi;
            float shift = b < 20.0 ? b : b - 20.0;
            hit = mod(floor(word / exp2(shift)), 2.0);
        }
        
        Mask3 = max(Mask3, hit);
    }
}
{
    vec2 q = vec2((UV.x - 0.64) / 0.020408, (UV.y - 0.64) / 0.035);
    if (q.y >= 0.0 && q.y < 1.0 && q.x >= 0.0 && q.x < 11.0)
    {
        float ci = floor(q.x);
        float px = floor(fract(q.x) * 6.0);
        float py = floor(q.y * 7.0);
        float glo = 0.0;
        float ghi = 0.0;
        if (ci > -0.5 && ci < 0.5) { glo = 67720.0; ghi = 8322.0; }
        if (ci > 0.5 && ci < 1.5) { glo = 135310.0; ghi = 14468.0; }
        if (ci > 1.5 && ci < 2.5) { glo = 135327.0; ghi = 4228.0; }
        if (ci > 2.5 && ci < 3.5) { glo = 2180.0; ghi = 0.0; }
        if (ci > 3.5 && ci < 4.5) { glo = 459838.0; ghi = 15888.0; }
        if (ci > 5.5 && ci < 6.5) { glo = 492607.0; ghi = 1057.0; }
        if (ci > 6.5 && ci < 7.5) { glo = 135310.0; ghi = 14468.0; }
        if (ci > 7.5 && ci < 8.5) { glo = 708145.0; ghi = 17977.0; }
        if (ci > 8.5 && ci < 9.5) { glo = 492607.0; ghi = 31777.0; }
        if (ci > 9.5 && ci < 10.5) { glo = 270466.0; ghi = 2184.0; }
        float hit = 0.0;
        if (px < 5.0)

        {
            float b = py * 5.0 + px;
            float word = b < 20.0 ? glo : ghi;
            float shift = b < 20.0 ? b : b - 20.0;
            hit = mod(floor(word / exp2(shift)), 2.0);
        }
        
        Mask3 = max(Mask3, hit);
    }
}
}

void sgCustom_Tally_77359(vec2 UV, out float Tally)
{
vec2 p = UV + vec2(sin(UV.y * 40.0) * 0.002, sin(UV.x * 37.0) * 0.002);
float tally = 0.0;
for (int i = 0; i < 47; i++)
{
    float fi = float(i);
    float group = floor(fi / 5.0);
    float k = mod(fi, 5.0);
    vec2 o = vec2(0.06 + mod(group, 5.0) * 0.105 + k * 0.016, 0.55 + floor(group / 5.0) * 0.14);
    float wob = sin(fi * 7.1) * 0.004;
    if (k < 3.5)
    {
        float stroke = step(abs(p.x - o.x - (p.y - o.y) * 0.08 - wob), 0.0035) * step(o.y, p.y) * step(p.y, o.y + 0.1);
        tally = max(tally, stroke);
    }
    else
    {
        vec2 a = vec2(o.x - 0.07, o.y + 0.08);
        vec2 b = vec2(o.x + 0.005, o.y + 0.02);
        vec2 pa = p - a;
        vec2 ba = b - a;
        float t = clamp(dot(pa, ba) / dot(ba, ba), 0.0, 1.0);
        tally = max(tally, step(length(pa - ba * t), 0.0035));
    }
}
Tally = tally;
}


void main()
{
	vec4 sg_fragCoord = gl_FragCoord;
	DecalGeometry sgDecal;
	if (!decalGeometry(gl_FragCoord.xy, sgDecal))
	{
		discard;
	}
	vec2 sg_UV0 = sgDecal.uv;
	vec3 sg_PositionObject = sgDecal.local;
	float sg_DecalFade = sgDecal.fade;

	// Marker #3
	float n3_Mask1;
	float n3_Mask2;
	float n3_Mask3;
	sgCustom_Marker_19759(sg_UV0, n3_Mask1, n3_Mask2, n3_Mask3);
	// Tally #4
	float n4_Tally;
	sgCustom_Tally_77359(sg_UV0, n4_Tally);
	// Add #5
	float n5_Out = n3_Mask1 + n4_Tally;
	// Multiply #7
	vec4 n7_Out = vec4_splat(n5_Out) * vec4(0.00393593963, 0.0196066499, 0.318546832, 1.0);
	// Multiply #9
	vec4 n9_Out = vec4_splat(n3_Mask2) * vec4(0.522521615, 0.00393593963, 0.00393593963, 1.0);
	// Add #10
	vec4 n10_Out = n7_Out + n9_Out;
	// Multiply #12
	vec4 n12_Out = vec4_splat(n3_Mask3) * vec4(0.00393593963, 0.132868335, 0.0196066499, 1.0);
	// Add #13
	vec4 n13_Out = n10_Out + n12_Out;
	// Add #14
	float n14_Out = n5_Out + n3_Mask2;
	// Add #15
	float n15_Out = n14_Out + n3_Mask3;
	// Saturate #16
	float n16_Out = clamp(n15_Out, 0.0, 1.0);
	// Multiply #18
	float n18_Out = n16_Out * sg_DecalFade;
	// Outputs
	vec3 sgOut_BaseColor = (n13_Out).xyz;
	float sgOut_Alpha = n18_Out;
	vec3 sgOut_Normal = vec3(0.0, 0.0, 1.0);
	float sgOut_Metallic = 0.0;
	float sgOut_Roughness = 0.400000006;
	vec3 sgOut_Emission = vec3(0.0, 0.0, 0.0);

	float alpha = sgOut_Alpha * sgDecal.fade;
	if (alpha <= 0.001)
	{
		discard;
	}
	vec3 N = decalWorldNormal(sgDecal, sgSafeNormalize(sgOut_Normal));
	vec3 color = shadeDecal(sgDecal, sgOut_BaseColor, N, sgOut_Metallic, sgOut_Roughness, sgOut_Emission, gl_FragCoord.xy);
	gl_FragColor = vec4(color, alpha);
}
