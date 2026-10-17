// Generated from Assets/ShaderGraphs/LostTemple/Caustics.shadergraph by the shader graph compiler: edit the graph, not this file.
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
// u_sgParams[0]: Caustic Color (Vector 3)
// u_sgParams[1]: Intensity (Float)
// u_sgParams[2]: Scale (Float)
// u_sgParams[3]: Speed (Float)

void sgCustom_Caustics_23316(vec2 Position, float Time, out float Light)
{
vec2 p = mod(Position * 6.2831853, vec2_splat(6.2831853)) - vec2_splat(250.0);
vec2 i = p;
float c = 1.0;
float strength = 0.005;
for (int n = 0; n < 4; n++)
{
    float t = Time * (1.0 - (3.5 / float(n + 1)));
    i = p + vec2(cos(t - i.x) + sin(t + i.y), sin(t - i.y) + cos(t + i.x));
    c += 1.0 / length(vec2(p.x / (sin(i.x + t) / strength), p.y / (cos(i.y + t) / strength)));
}
c /= 4.0;
c = 1.17 - pow(c, 1.4);
Light = pow(abs(c), 8.0);
}


void main()
{
	vec4 sg_fragCoord = gl_FragCoord;
	DecalGeometry sgDecal;
	if (!decalGeometry(gl_FragCoord.xy, sgDecal))
	{
		discard;
	}
	vec3 sg_PositionObject = sgDecal.local;
	vec3 sg_PositionWorld = sgDecal.worldPos;
	float sg_Time = u_time.y;
	float sg_DeltaTime = u_time.x;
	float sg_DecalFade = sgDecal.fade;

	// Swizzle .xz #7
	vec2 n7_Out = (vec4(sg_PositionWorld, 1.0)).xz;
	// Multiply #8
	vec2 n8_Out = n7_Out * vec2_splat(u_sgParams[2].x);
	// Multiply #10
	float n10_Out = sg_Time * u_sgParams[3].x;
	// Caustics #11
	float n11_Light;
	sgCustom_Caustics_23316(n8_Out, n10_Out, n11_Light);
	// Multiply #17
	float n17_Out = n11_Light * sg_DecalFade;
	// Swizzle .xy #13
	vec2 n13_Out = (vec4(sg_PositionObject, 1.0)).xy;
	// Length #14
	float n14_Out = length(n13_Out);
	// Smoothstep #15
	float n15_Out = smoothstep(0.360000014, 0.5, n14_Out);
	// One Minus #16
	float n16_Out = 1.0 - n15_Out;
	// Multiply #18
	float n18_Out = n17_Out * n16_Out;
	// Multiply #19
	float n19_Out = n18_Out * 1.60000002;
	// Saturate #20
	float n20_Out = clamp(n19_Out, 0.0, 1.0);
	// Multiply #21
	vec3 n21_Out = u_sgParams[0].xyz * vec3_splat(n18_Out);
	// Multiply #22
	vec3 n22_Out = n21_Out * vec3_splat(u_sgParams[1].x);
	// Outputs
	vec3 sgOut_BaseColor = vec3(0.0, 0.0, 0.0);
	float sgOut_Alpha = n20_Out;
	vec3 sgOut_Normal = vec3(0.0, 0.0, 1.0);
	float sgOut_Metallic = 0.0;
	float sgOut_Roughness = 0.300000012;
	vec3 sgOut_Emission = n22_Out;

	float alpha = sgOut_Alpha * sgDecal.fade;
	if (alpha <= 0.001)
	{
		discard;
	}
	vec3 N = decalWorldNormal(sgDecal, sgSafeNormalize(sgOut_Normal));
	vec3 color = shadeDecal(sgDecal, sgOut_BaseColor, N, sgOut_Metallic, sgOut_Roughness, sgOut_Emission, gl_FragCoord.xy);
	gl_FragColor = vec4(color, alpha);
}
