$input v_worldPos, v_normal, v_tangent, v_bitangent, v_texcoord0, v_viewPos, v_objectPos, v_objectNormal

// Generated from Assets/ShaderGraphs/Examples/Dissolve.shadergraph by the shader graph compiler: edit the graph, not this file.
// Shadow caster: depth only; alpha-clipped graphs cut their holes here too.
#define SG_ALPHA_CLIP 1

#include "Common.sh"
#include "ShaderGraph/SGLib.sh"

uniform vec4 u_sgParams[16];
// u_sgParams[0]: Edge Width (Float)
// u_sgParams[1]: Edge Color (Vector 3)
// u_sgParams[2]: Base Color (Vector 3)


void main()
{
	vec4 sg_fragCoord = gl_FragCoord;
	bool sg_frontFacing = gl_FrontFacing;
	vec2 sg_UV0 = v_texcoord0;
	float sg_Time = u_time.y;
	float sg_DeltaTime = u_time.x;

	// Gradient Noise #2
	float n2_Out = sgGradientNoise(sg_UV0, 6.0);
	// Remap #8
	float n8_Out = 0.0500000007 + (sin(sg_Time) - (-1.0)) * (0.5 - 0.0500000007) / (1.0 - (-1.0));
	// Subtract #9
	float n9_Out = n2_Out - n8_Out;
	// Outputs
	float sgOut_Alpha = n9_Out;
	float sgOut_AlphaClipThreshold = 0.0;

#if SG_ALPHA_CLIP
	if (sgOut_Alpha < sgOut_AlphaClipThreshold)
	{
		discard;
	}
#endif
	gl_FragColor = vec4_splat(0.0);
}
