// Generated from Assets/ShaderGraphs/Tests/GlowRingDecal.shadergraph by the shader graph compiler: edit the graph, not this file.
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
// u_sgParams[0]: Glow (Vector 3)


void main()
{
	vec4 sg_fragCoord = gl_FragCoord;
	DecalGeometry sgDecal;
	if (!decalGeometry(gl_FragCoord.xy, sgDecal))
	{
		discard;
	}
	vec2 sg_UV0 = sgDecal.uv;
	float sg_Time = u_time.y;
	float sg_DeltaTime = u_time.x;

	// Ellipse #2
	float n2_Out = sgEllipse(sg_UV0, 0.949999988, 0.949999988);
	// Ellipse #3
	float n3_Out = sgEllipse(sg_UV0, 0.75, 0.75);
	// Subtract #4
	float n4_Out = n2_Out - n3_Out;
	// Remap #6
	float n6_Out = 1.0 + (sin(sg_Time) - (-1.0)) * (4.0 - 1.0) / (1.0 - (-1.0));
	// Multiply #8
	vec3 n8_Out = u_sgParams[0].xyz * vec3_splat(n6_Out);
	// Multiply #9
	vec3 n9_Out = n8_Out * vec3_splat(n4_Out);
	// Outputs
	vec3 sgOut_BaseColor = vec3(0.0399999991, 0.0399999991, 0.0500000007);
	float sgOut_Alpha = n4_Out;
	vec3 sgOut_Normal = vec3(0.0, 0.0, 1.0);
	float sgOut_Metallic = 0.0;
	float sgOut_Roughness = 0.5;
	vec3 sgOut_Emission = n9_Out;

	float alpha = sgOut_Alpha * sgDecal.fade;
	if (alpha <= 0.001)
	{
		discard;
	}
	vec3 N = decalWorldNormal(sgDecal, sgSafeNormalize(sgOut_Normal));
	vec3 color = shadeDecal(sgDecal, sgOut_BaseColor, N, sgOut_Metallic, sgOut_Roughness, sgOut_Emission, gl_FragCoord.xy);
	gl_FragColor = vec4(color, alpha);
}
