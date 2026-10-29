$input v_worldPos, v_normal, v_tangent, v_bitangent, v_texcoord0, v_viewPos, v_objectPos, v_objectNormal

// Generated from Assets/ShaderGraphs/Examples/SynthwaveTerrain.shadergraph by the shader graph compiler: edit the graph, not this file.
// Shadow caster: depth only; alpha-clipped graphs cut their holes here too.
#define SG_OFFSET_WORLD 1
#define SG_FOG 1

#include "Common.sh"
#include "ShaderGraph/SGLib.sh"
#include "Dither.sh"

uniform vec4 u_drawParams; // x screen-door fade (Dither.sh), per draw

uniform vec4 u_sgParams[16];
// u_sgParams[0]: Height (Float)
// u_sgParams[1]: Valley Width (Float)
// u_sgParams[2]: Noise Scale (Float)
// u_sgParams[3]: Speed (Float)
// u_sgParams[4]: Curvature (Float)
// u_sgParams[5]: Cell Size (Float)
// u_sgParams[6]: Line Width (Float)
// u_sgParams[7]: Low Color (Vector 3)
// u_sgParams[8]: High Color (Vector 3)
// u_sgParams[9]: Fill Color (Vector 3)


void main()
{
	if (ditherDrops(u_drawParams.x, gl_FragCoord.xy))
	{
		discard;
	}
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
