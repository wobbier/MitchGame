$input v_worldPos, v_normal, v_tangent, v_bitangent, v_texcoord0, v_viewPos, v_objectPos, v_objectNormal

// Generated from Assets/ShaderGraphs/LostTemple/FoliageCutout.shadergraph by the shader graph compiler: edit the graph, not this file.
// Shadow caster: depth only; alpha-clipped graphs cut their holes here too.
#define SG_ALPHA_CLIP 1
#define SG_OFFSET_WORLD 1

#include "Common.sh"
#include "ShaderGraph/SGLib.sh"

uniform vec4 u_sgParams[16];
SAMPLER2D(s_sgTex0, 0); // Albedo
// u_sgParams[0]: Tint (Vector 3)
// u_sgParams[1]: Wind Strength (Float)
// u_sgParams[2]: Wind Speed (Float)
// u_sgParams[3]: Sway Height (Float)


void main()
{
	vec4 sg_fragCoord = gl_FragCoord;
	bool sg_frontFacing = gl_FrontFacing;
	vec2 sg_UV0 = v_texcoord0;

	// Sample Texture 2D #49
	vec4 n49_RGBA = toLinear(texture2D(s_sgTex0, sg_UV0));
	// Outputs
	float sgOut_Alpha = n49_RGBA.w;
	float sgOut_AlphaClipThreshold = 0.449999988;

#if SG_ALPHA_CLIP
	if (sgOut_Alpha < sgOut_AlphaClipThreshold)
	{
		discard;
	}
#endif
	gl_FragColor = vec4_splat(0.0);
}
