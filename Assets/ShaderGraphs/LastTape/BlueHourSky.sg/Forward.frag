$input v_worldPos, v_normal, v_tangent, v_bitangent, v_texcoord0, v_viewPos, v_objectPos, v_objectNormal

// Generated from Assets/ShaderGraphs/LastTape/BlueHourSky.shadergraph by the shader graph compiler: edit the graph, not this file.

#include "Common.sh"
#include "Lighting.sh"
#include "Fog.sh"
#include "ShaderGraph/SGLib.sh"

uniform vec4 u_sgParams[16];

void sgCustom_LastLightOfSummer_62630(vec3 View, out vec3 Color)
{
vec3 direction = -View;
float elevation = clamp(direction.y,0.0,1.0);
vec3 dusk = mix(vec3(.075,.055,.12),vec3(.008,.019,.055),pow(elevation,.45));
vec2 spherical = vec2(atan2(direction.z,direction.x)/6.2831853+.5,asin(direction.y)/3.14159265+.5);
vec2 cell = floor(spherical*vec2(650.0,325.0));
vec2 within = fract(spherical*vec2(650.0,325.0))-vec2_splat(.5);
float seed = fract(sin(dot(cell,vec2(12.9898,78.233)))*43758.5453);
float stars = step(.996,seed)*(1.0-smoothstep(.02,.14,length(within)))*smoothstep(.05,.4,elevation);
vec3 moonDirection = normalize(vec3(.15,.32,.94));
float separation = length(direction-moonDirection);
float moon = 1.0-smoothstep(.017,.018,separation);
float halo = exp(-separation*38.0)*.03;
float haze = sgValueNoise(spherical*vec2(34.0,100.0),1.0)*(1.0-smoothstep(.0,.4,elevation))*.009;
Color = dusk + vec3_splat(stars*.28+halo+haze) + vec3(.62,.71,.79)*moon;
}


void main()
{
	vec4 sg_fragCoord = gl_FragCoord;
	bool sg_frontFacing = gl_FrontFacing;
	vec3 sg_CameraPosition = mul(u_invView, vec4(0.0, 0.0, 0.0, 1.0)).xyz;
	vec3 sg_ViewDirectionWorld = sgSafeNormalize(sg_CameraPosition - v_worldPos);

	// LastLightOfSummer #3
	vec3 n3_Color;
	sgCustom_LastLightOfSummer_62630(sg_ViewDirectionWorld, n3_Color);
	// Outputs
	vec3 sgOut_Color = n3_Color;
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
