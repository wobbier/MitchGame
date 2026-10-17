$input v_worldPos, v_normal, v_tangent, v_bitangent, v_texcoord0, v_viewPos, v_objectPos, v_objectNormal

// Generated from Assets/ShaderGraphs/LastTape/CRTAfterHours.shadergraph by the shader graph compiler: edit the graph, not this file.
#define SG_FOG 1

#include "Common.sh"
#include "Lighting.sh"
#include "Fog.sh"
#include "ShaderGraph/SGLib.sh"

uniform vec4 u_sgParams[16];
// u_sgParams[0]: Phosphor (Vector 3)
// u_sgParams[1]: Brightness (Float)

void sgCustom_NoSignal_81184(vec2 UV, float Clock, vec3 Tint, float Gain, out vec3 Color)
{
vec2 p = UV - vec2_splat(0.5);
float border = 1.0-smoothstep(0.44,0.5,max(abs(p.x),abs(p.y)));
float lines = .78 + .22*sin(UV.y*190.0*3.14159265);
float roll = 1.0-smoothstep(0.0,0.075,abs(UV.y-fract(Clock*.12)));
float n = fract(sin(dot(floor(UV*vec2(240.0,180.0)),vec2(12.9898,78.233))+floor(Clock*24.0))*43758.5453);
// Abstract terminal windows and cursor, with no extra screen texture.
float window = step(abs(UV.x-.5),.36)*step(abs(UV.y-.42),.28);
float textRows = step(.77,fract(UV.y*22.0))*step(UV.x,.7)*step(.2,UV.x)*step(.19,UV.y)*step(UV.y,.59);
float cursor = step(abs(UV.x-.3),.035)*step(abs(UV.y-.64),.008)*step(.3,fract(Clock));
vec3 display = Tint*(.10 + window*.13 + textRows*.30 + cursor*.7 + roll*.1 + n*.035);
Color = display*lines*border*Gain;
}


void main()
{
	vec4 sg_fragCoord = gl_FragCoord;
	bool sg_frontFacing = gl_FrontFacing;
	vec2 sg_UV0 = v_texcoord0;
	float sg_Time = u_time.y;
	float sg_DeltaTime = u_time.x;

	// NoSignal #6
	vec3 n6_Color;
	sgCustom_NoSignal_81184(sg_UV0, sg_Time, u_sgParams[0].xyz, u_sgParams[1].x, n6_Color);
	// Outputs
	vec3 sgOut_Color = n6_Color;
	float sgOut_Alpha = 1.0;
	float sgOut_AlphaClipThreshold = 0.5;

#if SG_ALPHA_CLIP
	if (sgOut_Alpha < sgOut_AlphaClipThreshold)
	{
		discard;
	}
#endif

	vec3 color = sgOut_Color;
#if SG_FOG
	// Opaque surfaces are fogged by the fog pass; transparent ones (drawn after it) fog themselves.
	vec3 cameraPos = mul(u_invView, vec4(0.0, 0.0, 0.0, 1.0)).xyz;
	vec3 sunColor = u_lightParams.x > 0.5 ? directionalRadiance(0, v_worldPos) : vec3_splat(0.0);
	vec4 fog = fogForward(cameraPos, v_worldPos, sunColor, u_dirLightDirection[0].xyz);
	color = color * fog.a + fog.rgb;
#endif
	gl_FragColor = vec4(color, sgOut_Alpha);
}
