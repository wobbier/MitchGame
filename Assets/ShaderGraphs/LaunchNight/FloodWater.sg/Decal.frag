// Generated from Assets/ShaderGraphs/LaunchNight/FloodWater.shadergraph by the shader graph compiler: edit the graph, not this file.
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
// u_sgParams[0]: Water Color (Vector 3)
// u_sgParams[1]: Ripples (Float)
// u_sgParams[2]: Edge Noise (Float)

void sgCustom_Drips_89777(vec2 World, float Time, out float Ripple)
{
float h = 0.0;
vec2 g = World * 1.6;
for (int i = 0; i < 2; i++)
{
    vec2 id = floor(g + vec2_splat(float(i) * 0.5));
    vec2 fp = fract(g + vec2_splat(float(i) * 0.5)) - vec2_splat(0.5);
    float n = fract(sin(dot(id, vec2(12.9898, 78.233)) + float(i) * 7.1) * 43758.5453);
    float life = fract(Time * 0.9 + n);
    vec2 o = vec2(fract(n * 13.1), fract(n * 71.7)) * 0.5 - vec2_splat(0.25);
    float d = length(fp - o);
    float ring = sin((d - life * 0.45) * 70.0) * (1.0 - smoothstep(0.0, 0.06, abs(d - life * 0.45)));
    h += ring * (1.0 - life) * step(0.25, n);
}
Ripple = h * 0.5 + 0.5;
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
	vec3 sg_NormalWorld = sgDecal.normal;
	vec3 sg_TangentWorld = sgDecal.tangent;
	vec3 sg_BitangentWorld = sgDecal.bitangent;
	float sg_Time = u_time.y;
	float sg_DeltaTime = u_time.x;
	float sg_DecalFade = sgDecal.fade;

	// Swizzle .xy #6
	vec2 n6_Out = (vec4(sg_PositionObject, 1.0)).xy;
	// Multiply #7
	vec2 n7_Out = n6_Out * vec2(2.0, 2.0);
	// Length #13
	float n13_Out = length(n7_Out);
	// Swizzle .xz #9
	vec2 n9_Out = (vec4(sg_PositionWorld, 1.0)).xz;
	// Fractal Noise #10
	float n10_Out = sgFractalNoise(n9_Out, 0.899999976, 4.0, 2.0, 0.5);
	// Subtract #11
	float n11_Out = n10_Out - 0.5;
	// Multiply #12
	float n12_Out = n11_Out * u_sgParams[2].x;
	// Add #14
	float n14_Out = n13_Out + n12_Out;
	// Smoothstep #15
	float n15_Out = smoothstep(0.720000029, 0.899999976, n14_Out);
	// One Minus #16
	float n16_Out = 1.0 - n15_Out;
	// Multiply #21
	float n21_Out = n16_Out * sg_DecalFade;
	// Multiply #22
	float n22_Out = n21_Out * 0.920000017;
	// Drips #18
	float n18_Ripple;
	sgCustom_Drips_89777(n9_Out, sg_Time, n18_Ripple);
	// Multiply #19
	float n19_Out = n18_Ripple * u_sgParams[1].x;
	// Normal From Height #20
	vec3 n20_Out = sgWorldToTangent(sgNormalFromHeight(n19_Out, 0.25, sg_PositionWorld, sg_NormalWorld), sg_TangentWorld, sg_BitangentWorld, sg_NormalWorld);
	// Outputs
	vec3 sgOut_BaseColor = u_sgParams[0].xyz;
	float sgOut_Alpha = n22_Out;
	vec3 sgOut_Normal = n20_Out;
	float sgOut_Metallic = 0.0;
	float sgOut_Roughness = 0.0299999993;
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
