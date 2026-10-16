// Generated from Assets/ShaderGraphs/Examples/Scorch.shadergraph by the shader graph compiler: edit the graph, not this file.
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


void main()
{
	vec4 sg_fragCoord = gl_FragCoord;
	DecalGeometry sgDecal;
	if (!decalGeometry(gl_FragCoord.xy, sgDecal))
	{
		discard;
	}
	vec2 sg_UV0 = sgDecal.uv;

	// Subtract #5
	vec2 n5_Out = sg_UV0 - vec2(0.5, 0.5);
	// Length #6
	float n6_Out = length(n5_Out);
	// Remap #7
	float n7_Out = 1.20000005 + (n6_Out - 0.0) * ((-0.200000003) - 1.20000005) / (0.5 - 0.0);
	// Fractal Noise #4
	float n4_Out = sgFractalNoise(sg_UV0, 5.0, 5.0, 2.0, 0.5);
	// Add #8
	float n8_Out = n7_Out + n4_Out;
	// Smoothstep #9
	float n9_Out = smoothstep(0.899999976, 1.29999995, n8_Out);
	// Smoothstep #11
	float n11_Out = smoothstep(0.850000024, 1.0, n8_Out);
	// Subtract #12
	float n12_Out = n11_Out - n9_Out;
	// Multiply #14
	vec3 n14_Out = vec3_splat(n12_Out) * vec3(3.0, 0.800000012, 0.100000001);
	// Outputs
	vec3 sgOut_BaseColor = vec3(0.0199999996, 0.0179999992, 0.0149999997);
	float sgOut_Alpha = n9_Out;
	vec3 sgOut_Normal = vec3(0.0, 0.0, 1.0);
	float sgOut_Metallic = 0.0;
	float sgOut_Roughness = 0.949999988;
	vec3 sgOut_Emission = n14_Out;

	float alpha = sgOut_Alpha * sgDecal.fade;
	if (alpha <= 0.001)
	{
		discard;
	}
	vec3 N = decalWorldNormal(sgDecal, sgSafeNormalize(sgOut_Normal));
	vec3 color = shadeDecal(sgDecal, sgOut_BaseColor, N, sgOut_Metallic, sgOut_Roughness, sgOut_Emission, gl_FragCoord.xy);
	gl_FragColor = vec4(color, alpha);
}
