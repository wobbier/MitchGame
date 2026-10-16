$input v_worldPos, v_normal, v_tangent, v_bitangent, v_texcoord0, v_viewPos, v_objectPos, v_objectNormal

// Generated from Assets/ShaderGraphs/Tests/WobbleChecker.shadergraph by the shader graph compiler: edit the graph, not this file.
// Shadow caster: depth only; alpha-clipped graphs cut their holes here too.

#include "Common.sh"
#include "ShaderGraph/SGLib.sh"

uniform vec4 u_sgParams[16];
// u_sgParams[0]: Tint (Vector 3)
// u_sgParams[1]: Wobble (Float)


void main()
{
	vec4 sg_fragCoord = gl_FragCoord;
	bool sg_frontFacing = gl_FrontFacing;

	// Outputs
	float sgOut_Alpha = 1.0;
	float sgOut_AlphaClipThreshold = 0.5;

#if SG_ALPHA_CLIP
	if (sgOut_Alpha < sgOut_AlphaClipThreshold)
	{
		discard;
	}
#endif
	gl_FragColor = vec4_splat(0.0);
}
